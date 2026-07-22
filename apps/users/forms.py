from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "w-full px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors"
                }
            )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "bio", "avatar"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors"
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors"
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "w-full px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text focus:outline-none focus:border-gb-accent transition-colors resize-none",
                }
            ),
        }
