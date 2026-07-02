---
title: Installation Guide
order: 1
---

# Installation Guide

Follow the steps below to set up the Logbook development environment on your local machine.

## Prerequisites

Before getting started, ensure you have the following installed:

- Python 3.10 or later
- Node.js and npm
- Git

## 1. Clone the Repository

```bash
git clone https://github.com/opu-hossain/logbook.git
cd logbook
```

## 2. Create a Python Virtual Environment

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (Command Prompt)

```cmd
python -m venv venv
venv\Scripts\activate
```

### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

## 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 4. Install Frontend Dependencies

```bash
npm install
```

## 5. Apply Database Migrations

```bash
python manage.py migrate
```

## 6. Start the Development Environment

Since Logbook uses Django for the backend and Tailwind CSS for styling, you'll typically run two processes during development.

### Terminal 1 — Django Development Server

```bash
python manage.py runserver
```

The application will be available at:

```
http://127.0.0.1:8000/
```

### Terminal 2 — Tailwind CSS Watcher

```bash
npm run dev
```

This command watches your CSS files and automatically rebuilds Tailwind whenever changes are detected.

## Production CSS Build

To generate an optimized production CSS bundle, run:

```bash
npm run build
```

## Project Structure

```
logbook/
├── apps/               # Django applications
├── config/             # Project configuration
├── docs/               # Documentation
├── static/             # Static assets
├── templates/          # HTML templates
├── manage.py
├── requirements.txt
└── package.json
```

## Troubleshooting

### Virtual environment is not activated

Make sure your terminal prompt shows the virtual environment before installing packages or running Django commands.

### Database migration issues

If migrations fail, ensure all dependencies have been installed successfully:

```bash
pip install -r requirements.txt
```

Then retry:

```bash
python manage.py migrate
```

### Tailwind changes are not updating

Verify that the Tailwind watcher is running:

```bash
npm run dev
```

If the issue persists, reinstall the frontend dependencies:

```bash
rm -rf node_modules package-lock.json
npm install
```
