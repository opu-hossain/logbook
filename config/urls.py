"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth import views as auth_views

from apps.blog.feeds import LatestPostsFeed
from apps.blog.views import (
    home,
    markdown_preview,
    post_detail,
    blog,
    search,
    post_create,
    post_edit,
    post_delete,
    image_upload,
    draft_autosave,
)
from apps.blog.sitemaps import PostSitemap

sitemaps = {"posts": PostSitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("blog/", blog, name="blog"),
    path("markdownx/", include("markdownx.urls")),
    path("post/<slug:slug>/", post_detail, name="post_detail"),
    path("search/", search, name="search"),
    path("feed/", LatestPostsFeed(), name="feed"),
    path("auth/", include("apps.accounts.urls")),
    # [sitemap-path]
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # [email]
    # [password reset path's]
    path(
        "auth/password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "auth/password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "auth/password-reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "auth/password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # post for users
    path("write/", post_create, name="post_create"),
    path("post/<slug:slug>/edit/", post_edit, name="post_edit"),
    path("post/<slug:slug>/delete/", post_delete, name="post_delete"),
    path("api/upload-image/", image_upload, name="image_upload"),
    path("api/draft/autosave/", draft_autosave, name="draft_autosave"),
    path("api/preview-markdown/", markdown_preview, name="markdown_preview"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
