from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
    path("author/<str:username>/", views.author_profile_view, name="author_profile"),
    path("github/connect/", views.github_connect, name="github_connect"),
    path("github/callback/", views.github_callback, name="github_callback"),
    path("github/disconnect/", views.github_disconnect, name="github_disconnect"),
]
