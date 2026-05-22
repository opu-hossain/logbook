from django.shortcuts import get_object_or_404, render
from .models import Post

# Create your views here.


def home(request):
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-created_at")
    return render(request, "home.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLISHED)
    return render(request, "detail.html", {"post": post})
