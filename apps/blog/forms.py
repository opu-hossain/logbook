from logging import PlaceHolder
from django import forms
from .models import Comment


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
