from django import forms
from .models import Comment, Post, Category


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "placeholder": "Write a comment...",
                    "rows": 4,
                    "class": "w-full px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors resize-none",
                }
            ),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "category",
            "tags",
            "featured_image",
            "meta_description",
            "body",
            "content_type",
            "status",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Post title...",
                    "class": "w-full px-4 py-2 text-lg font-semibold rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors",
                }
            ),
            "meta_description": forms.TextInput(
                attrs={
                    "placeholder": "SEO description (max 160 characters)...",
                    "class": "w-full px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors",
                    "maxlength": "160",
                }
            ),
            "body": forms.Textarea(
                attrs={
                    "id": "post-body",
                    "class": "hidden",
                    "rows": 20,
                }
            ),
            "content_type": forms.HiddenInput(),
            "status": forms.Select(
                attrs={
                    "class": "px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors",
                }
            ),
            "featured_image": forms.FileInput(
                attrs={
                    "class": "text-sm text-gb-subtext dark:text-gb-dark-subtext file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-sm file:bg-gb-accent file:text-gb-bg dark:file:text-gb-dark-bg cursor-pointer",
                    "accept": "image/*",
                }
            ),
        }
