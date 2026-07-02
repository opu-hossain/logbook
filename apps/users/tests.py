from urllib.parse import parse_qs, urlparse
from unittest.mock import patch, PropertyMock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import GitHubAccount


class GitHubConnectViewTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            email="alice@example.com",
            password="test-pass-12345",
        )
        self.client.force_login(self.user)

    @override_settings(
        GITHUB_OAUTH_CLIENT_ID="your_client_id",
        GITHUB_OAUTH_CLIENT_SECRET="your_client_secret",
        GITHUB_OAUTH_REDIRECT_URI="http://localhost:8000/user/github/callback/",
    )
    def test_placeholder_github_oauth_settings_still_redirect_to_github(self):
        response = self.client.get(reverse("github_connect"))

        self.assertEqual(response.status_code, 302)

        parsed_url = urlparse(response.url)
        self.assertEqual(parsed_url.netloc, "github.com")
        self.assertEqual(parsed_url.path, "/login/oauth/authorize")

        params = parse_qs(parsed_url.query)
        self.assertEqual(params["client_id"], ["your_client_id"])
        self.assertEqual(
            params["redirect_uri"],
            ["http://localhost:8000/user/github/callback/"],
        )
        self.assertEqual(params["scope"], ["repo"])
        self.assertTrue(params["state"])

    @override_settings(
        GITHUB_OAUTH_CLIENT_ID="gho_realclientid",
        GITHUB_OAUTH_CLIENT_SECRET="super-secret-value",
        GITHUB_OAUTH_REDIRECT_URI="",
    )
    def test_github_connect_uses_the_real_callback_route(self):
        response = self.client.get(reverse("github_connect"))

        self.assertEqual(response.status_code, 302)

        parsed_url = urlparse(response.url)
        self.assertEqual(parsed_url.netloc, "github.com")
        self.assertEqual(parsed_url.path, "/login/oauth/authorize")

        params = parse_qs(parsed_url.query)
        self.assertEqual(params["client_id"], ["gho_realclientid"])
        self.assertEqual(
            params["redirect_uri"],
            ["http://testserver/user/github/callback/"],
        )
        self.assertEqual(params["scope"], ["repo"])
        self.assertTrue(params["state"])

    @patch("apps.users.views.fetch_owned_repositories")
    def test_profile_view_loads_owned_repositories(self, mock_fetch_owned_repositories):
        mock_fetch_owned_repositories.return_value = [
            {
                "full_name": "alice/private-repo",
                "html_url": "https://github.com/alice/private-repo",
                "description": "Private repo",
                "private": True,
                "default_branch": "main",
            }
        ]

        account = GitHubAccount.objects.create(
            user=self.user,
            github_id=123,
            github_username="alice",
            access_token="encrypted-placeholder",
            scope="repo",
        )

        with patch.object(GitHubAccount, "token", new_callable=PropertyMock) as mock_token:
            mock_token.return_value = "test-token"
            response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("github_repositories", response.context)
        self.assertEqual(
            response.context["github_repositories"][0]["full_name"],
            "alice/private-repo",
        )
        mock_fetch_owned_repositories.assert_called_once_with("test-token")
