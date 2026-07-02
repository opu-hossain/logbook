import secrets
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm, ProfileEditForm
from .models import User, GitHubAccount
from .services import fetch_owned_repositories
from apps.blog.models import Post

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"


def _github_callback_url(request):
    configured_url = getattr(settings, "GITHUB_OAUTH_REDIRECT_URI", "")
    if configured_url:
        return configured_url
    return request.build_absolute_uri(reverse("github_callback"))

# Create your views here.


@login_required
def profile_view(request):
    comments = request.user.comments.filter(approved=True).order_by("created_at")

    status_filter = request.GET.get("status", "all")
    posts = Post.objects.filter(author=request.user).order_by("-created_at")
    if status_filter != "all":
        posts = posts.filter(status=status_filter.upper())

    context = {
        "comments": comments,
        "posts": posts,
        "status_filter": status_filter,
        "status_choices": Post.Status.choices,
    }

    github_account = getattr(request.user, "github_account", None)
    if github_account:
        try:
            context["github_repositories"] = fetch_owned_repositories(
                github_account.token
            )
        except requests.RequestException:
            context["github_repositories"] = []
            messages.error(
                request,
                "GitHub repos could not be loaded right now. Try connecting again.",
            )
    else:
        context["github_repositories"] = []

    if request.headers.get("HX-Request"):
        return render(request, "partials/user_posts_list.html", context)

    return render(request, "users/profile.html", context)


@login_required
def profile_edit_view(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "users/profile_edit.html", {"form": form})


def author_profile_view(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author, status=Post.Status.PUBLISHED).order_by(
        "-created_at"
    )
    return render(
        request, "users/author_profile.html", {"author": author, "posts": posts}
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect("home")

    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get("next", "home")
            return redirect(next_url)
    else:
        form = AuthenticationForm()
        for field in form.fields.values():
            field.widget.attrs.update(
                {
                    "class": "w-full px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors"
                }
            )
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


@login_required
def github_connect(request):
    state = secrets.token_urlsafe(32)
    request.session["github_oauth_state"] = state
    redirect_uri = _github_callback_url(request)
    params = {
        "client_id": settings.GITHUB_OAUTH_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": "repo",
        "state": state,
    }
    return redirect(f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}")


@login_required
def github_callback(request):
    expected_state = request.session.pop("github_oauth_state", None)
    state = request.GET.get("state")
    code = request.GET.get("code")
    redirect_uri = _github_callback_url(request)

    if not state or state != expected_state:
        messages.error(
            request,
            "GitHub connection failed — the request could not be verified. Try again.",
        )
        return redirect("profile")
    if not code:
        messages.error(request, "GitHub connection was cancelled or failed.")
        return redirect("profile")

    token_resp = requests.post(
        GITHUB_TOKEN_URL,
        data={
            "client_id": settings.GITHUB_OAUTH_CLIENT_ID,
            "client_secret": settings.GITHUB_OAUTH_CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri,
        },
        headers={"Accept": "application/json"},
        timeout=15,
    )
    access_token = token_resp.json().get("access_token")
    if not access_token:
        messages.error(
            request,
            "GitHub didn't return an access token. Please try connecting again.",
        )
        return redirect("profile")

    user_resp = requests.get(
        GITHUB_USER_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=15,
    )
    user_resp.raise_for_status()
    gh_user = user_resp.json()

    try:
        account, _ = GitHubAccount.objects.update_or_create(
            user=request.user,
            defaults={"github_id": gh_user["id"], "github_username": gh_user["login"]},
        )
    except IntegrityError:
        messages.error(
            request, "This GitHub account is already linked to another Logbook account."
        )
        return redirect("profile")

    account.set_token(access_token)
    account.scope = token_resp.json().get("scope", "")
    account.save(update_fields=["access_token", "scope"])
    messages.success(request, f"Connected to GitHub as @{gh_user['login']}.")
    return redirect("profile")


@login_required
def github_disconnect(request):
    GitHubAccount.objects.filter(user=request.user).delete()
    messages.success(request, "Disconnected your GitHub account.")
    return redirect("profile")
