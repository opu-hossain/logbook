from django.shortcuts import get_object_or_404, render
from .models import Category, Post, Comment
from .forms import CommentForm
from django.core.paginator import Paginator
from django.db import models

# Create your views here.


def home(request):
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-created_at")
    return render(request, "home.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(approved=True)
    form = CommentForm()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            if request.headers.get("HX-Request"):
                return render(request, "partials/comment_success.html")
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
