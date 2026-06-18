from django.shortcuts import get_object_or_404, redirect, render
from .models import Category, Post
from .forms import CommentForm
from django.core.paginator import Paginator
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from markdownx.utils import markdownify
from django.http import HttpResponse, JsonResponse
import json

from .forms import CommentForm, PostForm

# Create your views here.


def home(request):
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-created_at")
    return render(request, "home.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(approved=True)
    form = CommentForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.name = request.user.get_full_name() or request.user.username
            comment.email = request.user.email
            comment.save()
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "partials/comment_success.html",
                    {
                        "post": post,
                        "toast_message": "Comment submitted! Awaiting approval.",
                        "toast_type": "success",
                    },
                )
        else:
            if request.headers.get("HX-Request"):
                return render(
                    request, "partials/comment_form.html", {"form": form, "post": post}
                )

    return render(
        request, "detail.html", {"post": post, "comments": comments, "form": form}
    )


def blog(request):
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-created_at")

    category_slug = request.GET.get("category")
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=active_category)
    categories = Category.objects.all()

    paginator = Paginator(posts, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "blog.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "active_category": active_category,
        },
    )


def search(request):
    query = request.GET.get("q", "")
    results = []
    if query:
        results = (
            Post.objects.filter(status=Post.Status.PUBLISHED)
            .filter(models.Q(title__icontains=query) | models.Q(body__icontains=query))
            .order_by("-created_at")
        )
        # print(f"Query: {query}, Results count: {results.count()}")
        # for post in results:
        #    print(f"  - {post.title}")

    if request.headers.get("HX-Request"):
        return render(
            request,
            "partials/search_results.html",
            {
                "results": results,
                "query": query,
            },
        )

    return render(request, "search.html", {"results": results, "query": query})


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, "Post published successfully!")
            return redirect("post_details", slug=post.slug)
        else:
            messages.error(request, "Please fix the errors!")
    else:
        form = PostForm()
    return render(
        request,
        "post_create.html",
        {"form": form, "editor_mode": request.user.editor_preference},
    )


@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            form.save_m2m()
            messages.success(request, "Post updated successfully!")
            return redirect("post_details", slug=post.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = PostForm(instance=post)
    return render(request, "post_create.html", {"form": form, "post": post})


@login_required
@require_POST
def image_upload(request):
    image = request.FILES.get("image")
    if not image:
        return JsonResponse({"error": "No image provided."}, status=400)

    path = default_storage.save(f"post_images/{image.name}", ContentFile(image.read()))
    url = request.build_absolute_uri(f"/media/{path}")
    return JsonResponse({"url": url})


@login_required
@require_POST
def markdown_preview(request):
    raw = request.POST.get("body", "")
    return HttpResponse(markdownify(raw))


@login_required
@require_POST
def draft_autosave(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    slug = data.get("slug")
    body = data.get("body", "")
    content_type = data.get("content_type", "markdown")

    if slug:
        post = get_object_or_404(Post, slug=slug, author=request.user)
        post.body = body
        post.content_type = content_type
        post.status = Post.Status.DRAFT
        post.save(update_fields=["body", "content_type", "status"])
        return JsonResponse({"status": "saved", "slug": post.slug})
    else:
        title = data.get("title", "").strip()
        if not title:
            return JsonResponse({"status": "skipped", "reason": "no title yet"})

        post = Post.objects.create(
            title=title,
            body=body,
            content_type=content_type,
            author=request.user,
            status=Post.Status.DRAFT,
        )
        return JsonResponse({"status": "saved", "slug": post.slug})
