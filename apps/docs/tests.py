from unittest.mock import patch, PropertyMock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.users.models import GitHubAccount

from .models import Project


class ProjectCreateViewTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username="alice",
			email="alice@example.com",
			password="test-pass-12345",
		)
		self.client.force_login(self.user)

	def _create_github_account(self):
		return GitHubAccount.objects.create(
			user=self.user,
			github_id=123,
			github_username="alice",
			access_token="encrypted-placeholder",
			scope="repo",
		)

	@patch("apps.docs.views.fetch_owned_repositories")
	def test_project_create_get_requires_github_account_repositories(self, mock_fetch):
		mock_fetch.return_value = [
			{
				"full_name": "alice/private-repo",
				"private": True,
				"default_branch": "main",
			}
		]
		self._create_github_account()

		with patch.object(GitHubAccount, "token", new_callable=PropertyMock) as mock_token:
			mock_token.return_value = "test-token"
			response = self.client.get(reverse("project_create"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "alice/private-repo")

	@patch("apps.docs.views.fetch_owned_repositories")
	@patch("apps.docs.views.sync_project")
	def test_private_repo_forces_private_visibility(self, mock_sync, mock_fetch):
		mock_fetch.return_value = [
			{
				"full_name": "alice/private-repo",
				"private": True,
				"default_branch": "main",
			}
		]
		self._create_github_account()

		with patch.object(GitHubAccount, "token", new_callable=PropertyMock) as mock_token:
			mock_token.return_value = "test-token"
			response = self.client.post(
				reverse("project_create"),
				{
					"repo_full_name": "alice/private-repo",
					"name": "",
					"default_branch": "main",
					"docs_path": "docs",
				},
			)

		self.assertEqual(Project.objects.count(), 1)
		project = Project.objects.get()
		self.assertFalse(project.is_public)
		self.assertTrue(project.github_private)
		self.assertEqual(response.status_code, 302)
		mock_sync.assert_called_once()

	@patch("apps.docs.views.fetch_owned_repositories")
	@patch("apps.docs.views.sync_project")
	def test_public_repo_starts_private(self, mock_sync, mock_fetch):
		mock_fetch.return_value = [
			{
				"full_name": "alice/public-repo",
				"private": False,
				"default_branch": "main",
			}
		]
		self._create_github_account()

		with patch.object(GitHubAccount, "token", new_callable=PropertyMock) as mock_token:
			mock_token.return_value = "test-token"
			self.client.post(
				reverse("project_create"),
				{
					"repo_full_name": "alice/public-repo",
					"name": "",
					"default_branch": "main",
					"docs_path": "docs",
				},
			)

		project = Project.objects.get()
		self.assertFalse(project.is_public)
		self.assertFalse(project.github_private)
		mock_sync.assert_called_once()

	def test_project_create_redirects_without_github_account(self):
		response = self.client.get(reverse("project_create"))
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse("profile"))

	def test_private_project_visibility_is_locked(self):
		project = Project.objects.create(
			owner=self.user,
			name="Private docs",
			slug="private-docs",
			github_owner="alice",
			github_repo="private-repo",
			github_private=True,
			is_public=False,
		)

		response = self.client.post(reverse("project_toggle_visibility", args=[project.slug]))

		project.refresh_from_db()
		self.assertFalse(project.is_public)
		self.assertEqual(response.status_code, 302)

	def test_project_docs_index_redirects_to_first_page_when_root_missing(self):
		project = Project.objects.create(
			owner=self.user,
			name="Private docs",
			slug="private-docs",
			github_owner="alice",
			github_repo="private-repo",
			github_private=False,
			is_public=True,
		)
		project.pages.create(
			file_path="docs/intro.md",
			slug_path="intro",
			title="Intro",
			nav_label="Intro",
			order=1,
			raw_markdown="# Intro",
		)

		response = self.client.get(reverse("project_docs_index", args=[project.slug]))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse("doc_page", args=[project.slug, "intro"]))
