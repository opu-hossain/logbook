import re

from django import forms

from .models import Project

INPUT_CLASS = (
    "w-full px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border "
    "bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text "
    "focus:outline-none focus:border-gb-accent transition-colors"
)

GITHUB_URL_RE = re.compile(r"^https?://github\.com/([^/\s]+)/([^/\s]+?)(?:\.git)?/?$")


class ProjectForm(forms.ModelForm):
    repo_url = forms.URLField(
        label="GitHub repository URL",
        widget=forms.URLInput(
            attrs={"placeholder": "https://github.com/owner/repo", "class": INPUT_CLASS}
        ),
    )

    class Meta:
        model = Project
        fields = ["name", "default_branch", "docs_path"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Leave blank to use the repo name",
                    "class": INPUT_CLASS,
                }
            ),
            "default_branch": forms.TextInput(
                attrs={"placeholder": "main", "class": INPUT_CLASS}
            ),
            "docs_path": forms.TextInput(
                attrs={"placeholder": "docs", "class": INPUT_CLASS}
            ),
        }

    def clean_repo_url(self):
        url = self.cleaned_data["repo_url"].strip()
        match = GITHUB_URL_RE.match(url)
        if not match:
            raise forms.ValidationError(
                "Enter a GitHub repo URL, e.g. https://github.com/owner/repo"
            )
        return match.groups()

    def save(self, commit=True):
        owner, repo = self.cleaned_data["repo_url"]
        instance = super().save(commit=False)
        instance.github_owner = owner
        instance.github_repo = repo
        if commit:
            instance.save()
        return instance
