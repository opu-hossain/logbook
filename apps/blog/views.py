from django.core import paginator
from django.shortcuts import get_object_or_404, render
from .models import Post
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
    paginator = Paginator(posts, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "blog.html", {"page_obj": page_obj})
