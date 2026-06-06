from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm, ProfileEditForm

# Create your views here.


@login_required
def profile_view(request):
    comments = request.user.comments.filter(approved=True).order_by("created_at")
    return render(request, "accounts/profile.html", {"comments": comments})


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
    return render(request, "accounts/profile_edit.html", {"form": form})


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
    return render(request, "accounts/register.html", {"form": form})


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
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")
