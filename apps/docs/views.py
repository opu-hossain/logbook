from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import DocPage, Project
from .services import SyncError, sync_project

# Create your views here.


@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user).order_by("-created_at")
    return render(request, "docs/project_list.html", {"projects": projects})


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            try:
                sync_project(project)
                messages.success(request, f'"{project.name}" connected and synced.')
            except SyncError as exc:
                messages.warning(
                    request, f"Project connected, but the first sync failed: {exc}"
                )
            return redirect("project_docs_index", project_slug=project.slug)
    else:
        form = ProjectForm()
    return render(request, "docs/project_create.html", {"form": form})


@login_required
@require_POST
def project_sync(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug, owner=request.user)
    try:
        sync_project(project)
        messages.success(request, f'"{project.name}" synced successfully.')
    except SyncError as exc:
        messages.error(request, f"Sync failed: {exc}")
    return redirect("project_list")


def doc_page(request, project_slug, page_path=""):
    project = get_object_or_404(Project, slug=project_slug)
    page = get_object_or_404(DocPage, project=project, slug_path=page_path.strip("/"))
    return render(request, "docs/doc_page.html", {"project": project, "page": page})
