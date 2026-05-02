# Exodus Attendance System

## Overview
A Django 5.2-based attendance management system ("Exodus") with a full HTMX + Alpine.js + Tailwind CSS frontend. Manages students, lecturers, courses, and attendance sessions with QR codes, two-factor authentication, and reporting.

## Architecture
- **Backend**: Django 5.2 (monolithic — Django serves both the API and the HTML frontend)
- **Frontend**: Django templates + HTMX + Alpine.js + Tailwind CSS + Flowbite
- **Database**: SQLite (development default), PostgreSQL via `DATABASE_URL` env var (production)
- **Auth**: Custom authentication backends (email, student ID, staff ID) + JWT (DRF) + session auth
- **Storage**: Local filesystem (dev), Cloudinary (production)
- **Email**: Console backend (dev), Brevo/Sendinblue via Anymail (production)

## Key Apps
- `attendance/` — Core models (Student, Lecturer, Course, Attendance, etc.), REST API views, serializers
- `frontend/` — HTMX-driven HTML views (login, dashboard, student/lecturer/course/attendance management)
- `attendance_system/` — Django project settings, URLs, Celery config, WSGI/ASGI

## Development Setup
- **Run server**: `python manage.py runserver 0.0.0.0:5000`
- **Build CSS/JS**: `npm run build` (Tailwind CSS + copies alpinejs/htmx/flowbite to static/)
- **Migrations**: `python manage.py migrate`
- **Static files**: `python manage.py collectstatic`

## Dependencies
- Python deps: installed from `requirements.txt` (note: `psycopg2` non-binary line is commented out — use `psycopg2-binary` instead)
- Node deps: `npm install` (tailwindcss, alpinejs, htmx.org, flowbite, concurrently)

## Workflow
- **Start application**: `python manage.py runserver 0.0.0.0:5000` — port 5000, webview

## Deployment
- Configured as `autoscale` with gunicorn: `gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 --timeout=120 attendance_system.wsgi`
- Set `DJANGO_SECRET_KEY`, `DATABASE_URL`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS` in production

## Replit-Specific Notes
- `ALLOWED_HOSTS = ['*']` in DEBUG mode for Replit proxy compatibility
- `CSRF_TRUSTED_ORIGINS` includes `*.replit.dev`, `*.repl.co`, `*.replit.app` in DEBUG mode
- Admin panel at `/exodus-manage/` (obfuscated from `/admin/`)
- Health check endpoint at `/health/`
- API docs (Swagger) at `/api/docs/`
