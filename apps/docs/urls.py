from django.urls import path
from . import views

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("new/", views.project_create, name="project_create"),
    path("<slug:project_slug>/sync/", views.project_sync, name="project_sync"),
    path(
        "<slug:project_slug>/toggle-visibility/",
        views.project_toggle_visibility,
        name="project_toggle_visibility",
    ),
    path("<slug:project_slug>/", views.doc_page, name="project_docs_index"),
    path("<slug:project_slug>/<path:page_path>/", views.doc_page, name="doc_page"),
]
