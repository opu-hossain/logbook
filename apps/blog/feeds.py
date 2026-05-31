from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Post
import re


class LatestPostsFeed(Feed):
    title = "Logbook"
    link = "/blog/"
    description = "Latest posts from Logbook."

    def items(self):
        return Post.objects.filter(status=Post.Status.PUBLISHED).order_by(
            "-created_at"
        )[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if item.meta_description:
            return item.meta_description

        text = item.body
        text = re.sub(r"#{1,6}\s*", "", text)
        text = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", text)
        text = re.sub(r"_{1,2}(.*?)_{1,2}", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        text = re.sub(r"`{1,3}.*?`{1,3}", "", text, flags=re.DOTALL)
        text = re.sub(r">\s*", "", text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        return text[:200]

    def item_link(self, item):
        return reverse("post_detail", args=[item.slug])
