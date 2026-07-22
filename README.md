# Logbook

Logbook is a documentation hub designed for developers and open-source projects. It syncs documentation directly from GitHub repositories and renders it into a clean, modern, and highly readable documentation website.

**Live Demo:** https://logbook-omkt.onrender.com

---

## Features

- **GitHub Repository Sync** — Automatically fetches and updates Markdown documentation from linked GitHub repositories.
- **Rich Markdown Rendering** — Parses Markdown and frontmatter to generate beautifully styled documentation pages.
- **OAuth Authentication** — Secure authentication and repository access using GitHub OAuth.
- **Media Management** — Cloudinary integration for scalable media storage and delivery.
- **Automated CI/CD** — Continuous integration and deployment with GitHub Actions and Render.

---

## Built With

- **Backend:** Django 5.2, Python
- **Database:** PostgreSQL (Production), SQLite (Development)
- **Styling:** Tailwind CSS
- **Static & Media:** WhiteNoise, Cloudinary
- **Infrastructure:** GitHub Actions, Render

---

## Local Installation

Follow these steps to run Logbook locally.

### 1. Clone the Repository

```bash
git clone https://github.com/opu-hossain/logbook.git
cd logbook
```

### 2. Create a Virtual Environment

Using a virtual environment is recommended.

```bash
python -m venv .venv
```

Activate it:

**Linux/macOS**

```bash
source .venv/bin/activate
```

**Windows**

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (alongside `manage.py`) and configure the following variables.

| Variable | Description |
|----------|-------------|
| `DEBUG` | Set to `True` for local development. |
| `SECRET_KEY` | Django secret key. |
| `DATABASE_URL` | Use `sqlite:///db.sqlite3` for local development. |
| `CLOUDINARY_URL` | Cloudinary connection string. |
| `GITHUB_OAUTH_CLIENT_ID` | GitHub OAuth application client ID. |
| `GITHUB_OAUTH_CLIENT_SECRET` | GitHub OAuth application client secret. |
| `GITHUB_TOKEN_ENCRYPTION_KEY` | Secure 32-byte Base64 key used to encrypt stored OAuth tokens. |
| `GITHUB_OAUTH_REDIRECT_URI` | OAuth callback URL (for example: `http://127.0.0.1:8000/users/oauth/callback/`). |

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser (Optional)

To access the Django admin interface:

```bash
python manage.py createsuperuser
```

### 7. Start the Development Server

```bash
python manage.py runserver --settings=config.settings.dev
```

The application will be available at:

```
http://127.0.0.1:8000
```

---

## Contributing

Contributions are welcome and greatly appreciated. To maintain code quality and ensure a consistent development experience, all pull requests must pass the project's automated CI pipeline.

### Development Workflow

1. **Fork the repository**

2. **Create a feature branch**

```bash
git checkout -b feature/amazing-feature
```

3. **Install development dependencies**

If additional development tools are required:

```bash
pip install -r requirements.txt
```

4. **Run Ruff**

This project uses Ruff for linting and formatting.

```bash
ruff check --fix .
```

Optionally, format the code:

```bash
ruff format .
```

5. **Run Django checks**

```bash
python manage.py check
```

6. **Run the test suite**

```bash
python manage.py test
```

7. **Commit your changes**

```bash
git commit -m "Add amazing feature"
```

8. **Push your branch**

```bash
git push origin feature/amazing-feature
```

9. **Open a Pull Request**

Please ensure:

- Code passes Ruff linting.
- All Django checks succeed.
- All tests pass.
- Your changes are clearly described.

---

## Deployment

Logbook is configured for automated deployment on Render.

### Production Stack

- **Application Hosting:** Render
- **Database:** PostgreSQL
- **Static Files:** WhiteNoise
- **Media Storage:** Cloudinary
- **CI/CD:** GitHub Actions

### Deployment Pipeline

Every push to the `main` branch triggers the GitHub Actions workflow, which:

1. Installs project dependencies.
2. Runs Ruff linting.
3. Executes Django system checks.
4. Runs the test suite.
5. Triggers the Render deployment webhook if all checks pass successfully.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
