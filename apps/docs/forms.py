from django import forms

from .models import Project

INPUT_CLASS = (
    "w-full px-3 py-2 text-sm rounded border border-gb-border dark:border-gb-dark-border "
    "bg-gb-surface dark:bg-gb-dark-surface text-gb-text dark:text-gb-dark-text "
    "focus:outline-none focus:border-gb-accent transition-colors"
)


class ProjectForm(forms.ModelForm):
    repo_full_name = forms.ChoiceField(
        label="GitHub repository",
        choices=(),
        widget=forms.Select(attrs={"class": INPUT_CLASS}),
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

    def __init__(self, *args, repositories=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.repositories = repositories or []
        self.repository_map = {}

        choices = [("", "Select one of your connected GitHub repositories")]
        for repo in self.repositories:
            full_name = repo["full_name"]
            privacy_label = "private" if repo.get("private") else "public"
            choices.append((full_name, f"{full_name} ({privacy_label})"))
            self.repository_map[full_name] = repo

        self.fields["repo_full_name"].choices = choices

    def clean_repo_full_name(self):
        full_name = self.cleaned_data["repo_full_name"]
        if full_name not in self.repository_map:
            raise forms.ValidationError(
                "Select a repository from your connected GitHub account."
            )
        return full_name

    def clean(self):
        cleaned_data = super().clean()
        full_name = cleaned_data.get("repo_full_name")
        if not full_name:
            return cleaned_data

        repo = self.repository_map.get(full_name)
        cleaned_data["_repo_data"] = repo
        return cleaned_data

    def save(self, commit=True):
        owner, repo = self.cleaned_data["repo_full_name"].split("/", 1)
        repo_data = self.cleaned_data.get("_repo_data") or self.repository_map.get(
            self.cleaned_data["repo_full_name"]
        )
        instance = super().save(commit=False)
        instance.github_owner = owner
        instance.github_repo = repo
        instance.github_private = bool(repo_data and repo_data.get("private"))
        instance.is_public = False
        if commit:
            instance.save()
        return instance
