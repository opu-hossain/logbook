"""GitHub account helpers for the users app."""

from __future__ import annotations

import requests

GITHUB_API = "https://api.github.com"


def fetch_owned_repositories(access_token: str) -> list[dict]:
    """Return repositories owned by the authenticated GitHub user.

    GitHub's OAuth repo scope is sufficient to read private repositories that the
    user owns or otherwise can access.
    """

    response = requests.get(
        f"{GITHUB_API}/user/repos",
        params={
            "affiliation": "owner",
            "per_page": 100,
            "sort": "updated",
            "direction": "desc",
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=15,
    )
    response.raise_for_status()
    repos = response.json()
    if not isinstance(repos, list):
        return []
    return repos
