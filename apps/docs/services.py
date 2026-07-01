import json
import re

import frontmatter
import requests
from django.db import transaction
from django.utils import timezone

from .models import DocPage, Project

GITHUB_API = "https://api.github.com"


class SyncError(Exception):
    """Raised for any recoverable sync failure — message is shown to the user."""


def sync_project(project: Project) -> None:
    project.sync_status = Project.SyncStatus.SYNCING
    project.sync_error = ""
    project.save(update_fields=["sync_status", "sync_error"])

    try:
        tree = _fetch_tree(project)
        md_files, category_files = _filter_docs_files(tree, project.docs_path)
        if not md_files:
            raise SyncError(
                f'No markdown files found under "{project.docs_path}/". '
                "Check the docs path and default branch."
            )
        categories = _fetch_categories(project, category_files)
        pages_data = _fetch_pages(project, md_files)
        _replace_pages(project, pages_data)

        project.nav_tree = _build_nav_tree(pages_data, categories)
        project.sync_status = Project.SyncStatus.SYNCED
        project.last_synced_at = timezone.now()
        project.save(update_fields=["nav_tree", "sync_status", "last_synced_at"])
    except SyncError as exc:
        project.sync_status = Project.SyncStatus.FAILED
        project.sync_error = str(exc)
        project.save(update_fields=["sync_status", "sync_error"])
        raise


def _fetch_tree(project):
    url = f"{GITHUB_API}/repos/{project.github_owner}/{project.github_repo}/git/trees/{project.default_branch}"
    resp = requests.get(url, params={"recursive": "1"}, timeout=15)
    if resp.status_code == 404:
        raise SyncError(
            "Repo or branch not found — check the owner/repo name and default branch."
        )
    if resp.status_code == 403:
        raise SyncError(
            "GitHub API rate limit hit (60 requests/hour for public access). Try again later."
        )
    resp.raise_for_status()
    data = resp.json()
    if data.get("truncated"):
        raise SyncError("This repo's file tree is too large for a single sync request.")
    return data["tree"]


def _filter_docs_files(tree, docs_path):
    prefix = docs_path.strip("/") + "/"
    md_files, category_files = [], []
    for entry in tree:
        if entry["type"] != "blob":
            continue
        path = entry["path"]
        if not path.startswith(prefix):
            continue
        rel = path[len(prefix) :]
        if rel.endswith(".md"):
            md_files.append(path)
        elif rel.rsplit("/", 1)[-1] == "_category.json":
            category_files.append(path)
    return md_files, category_files


def _fetch_raw(project, path):
    url = f"https://raw.githubusercontent.com/{project.github_owner}/{project.github_repo}/{project.default_branch}/{path}"
    resp = requests.get(url, timeout=15)
    if resp.status_code != 200:
        raise SyncError(f"Could not fetch {path} (HTTP {resp.status_code}).")
    return resp.text


def _humanize(name):
    name = re.sub(
        r"^\d+[-_.]?", "", name
    )  # strip leading "01-" style ordering prefixes
    return (name.replace("-", " ").replace("_", " ").strip().title()) or "Untitled"


def _fetch_categories(project, category_files):
    prefix = project.docs_path.strip("/") + "/"
    categories = {}
    for path in category_files:
        rel = path[len(prefix) :]
        folder = rel.rsplit("/", 1)[0] if "/" in rel else ""
        try:
            categories[folder] = json.loads(_fetch_raw(project, path))
        except ValueError:
            continue  # malformed _category.json — ignore, fall back to defaults
    return categories


def _fetch_pages(project, md_files):
    prefix = project.docs_path.strip("/") + "/"
    pages = []
    for path in md_files:
        post = frontmatter.loads(_fetch_raw(project, path))
        stem = path[len(prefix) :][:-3]  # strip docs/ prefix and ".md"

        if stem == "index":
            slug_path = ""
        elif stem.endswith("/index"):
            slug_path = stem[: -len("/index")]
        else:
            slug_path = stem

        folder = slug_path.rsplit("/", 1)[0] if "/" in slug_path else ""
        filename = stem.rsplit("/", 1)[-1]
        default_title = _humanize(filename)

        pages.append(
            {
                "file_path": path,
                "slug_path": slug_path,
                "folder": folder,
                "title": post.metadata.get("title") or default_title,
                "nav_label": post.metadata.get("nav_label")
                or post.metadata.get("title")
                or default_title,
                "order": post.metadata.get("order"),  # None if not set — resolved later
                "raw_markdown": post.content,
            }
        )
    return pages


@transaction.atomic
def _replace_pages(project, pages_data):
    project.pages.all().delete()
    DocPage.objects.bulk_create(
        [
            DocPage(
                project=project,
                file_path=d["file_path"],
                slug_path=d["slug_path"],
                title=d["title"],
                nav_label=d["nav_label"],
                order=d["order"] or 0,
                raw_markdown=d["raw_markdown"],
            )
            for d in pages_data
        ]
    )


def _build_nav_tree(pages_data, categories):
    folders = {}
    root = []

    def ensure_folder(path):
        if path in folders:
            return folders[path]
        cat = categories.get(path, {})
        label = cat.get("label") or _humanize(path.rsplit("/", 1)[-1])
        node = {
            "type": "folder",
            "path": path,
            "label": label,
            "order": cat.get("order", 9999),
            "children": [],
        }
        folders[path] = node
        parent = path.rsplit("/", 1)[0] if "/" in path else ""
        (root if parent == "" else ensure_folder(parent)["children"]).append(node)
        return node

    for d in pages_data:
        page_node = {
            "type": "page",
            "label": d["nav_label"],
            "slug": d["slug_path"],
            "order": d["order"] if d["order"] is not None else 9999,
        }
        (root if d["folder"] == "" else ensure_folder(d["folder"])["children"]).append(
            page_node
        )

    def sort_tree(nodes):
        nodes.sort(key=lambda n: (n["order"], n["label"].lower()))
        for n in nodes:
            if n["type"] == "folder":
                sort_tree(n["children"])

    sort_tree(root)
    return root
