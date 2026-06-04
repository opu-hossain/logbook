from logging import PlaceHolder
from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["name", "email", "body"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Your name",
                    "class": "w-full px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Your email (not published)",
                    "class": "w-full px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors",
                }
            ),
            "body": forms.Textarea(
                attrs={
                    "placeholder": "Write a comment...",
                    "rows": 4,
                    "class": "w-full px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors resize-none",
                }
            ),
        }
