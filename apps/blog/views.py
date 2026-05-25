from django.core import paginator
from django.shortcuts import get_object_or_404, render
from .models import Category, Post
from django.core.paginator import Paginator

# Create your views here.


def home(request):
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-created_at")
    return render(request, "home.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLISHED)
    return render(request, "detail.html", {"post": post})


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
