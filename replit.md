# Exodus Attendance System

## Overview
A Django 5.2-based attendance management system with a full HTMX + Alpine.js + Tailwind CSS frontend. Manages students, lecturers, courses, and attendance sessions with QR codes, two-factor authentication (WebAuthn biometric + TOTP), and reporting.

## Architecture
- **Backend**: Django 5.2 (monolithic — Django serves both the API and the HTML frontend)
- **Frontend**: Django templates + HTMX + Alpine.js + Tailwind CSS + Flowbite
- **Database**: SQLite (development default), PostgreSQL via `DATABASE_URL` env var (production)
- **Auth**: Custom authentication backends (email, student ID, staff ID) + JWT (DRF) + session auth
- **Storage**: Local filesystem (dev), Cloudinary (production)
- **Email**: Console backend (dev), Brevo/Sendinblue via Anymail (production)
- **Task queue**: Celery + Redis (bulk upload processing)

## Key Apps
- `attendance/` — Core models (Student, Lecturer, Course, Attendance, etc.), REST API views, serializers
- `frontend/` — HTMX-driven HTML views (login, dashboard, student/lecturer/course/attendance management)
- `attendance_system/` — Django project settings, URLs, Celery config, WSGI/ASGI

## Design System
All templates use a consistent design language (fully audited and upgraded across all 6 batches):
- **Cards**: `rounded-2xl bg-white/80 backdrop-blur-md border border-gray-100/60 shadow-lg`
- **Accent stripe**: `h-1 bg-gradient-to-r from-{color}-500 to-{color}-600` on card tops
- **Icon chips**: `rounded-xl bg-{color}-50 p-2.5`
- **Primary buttons**: `rounded-xl bg-brand-600 shadow-lg shadow-brand-500/20 hover:-translate-y-0.5`
- **Secondary buttons**: `rounded-xl border border-gray-200 bg-white/50 backdrop-blur-sm`
- **Back links**: `inline-flex items-center gap-1 text-sm font-medium text-brand-600`
- **Brand colour**: configured in `tailwind.config.js` as `brand` (maps to the primary indigo-based palette)
- **Dark mode**: full dark mode support on all components
- Intentional accent colours: stat cards use distinct per-card colours (indigo, violet, emerald, blue)

## Development Setup
- **Run server**: `python manage.py runserver 0.0.0.0:5000`
- **Build CSS/JS**: `npm run build` (Tailwind CSS + copies alpinejs/htmx/flowbite to static/)
- **Migrations**: `python manage.py migrate`
- **Static files**: `python manage.py collectstatic`

## Dependencies
- Python deps: installed from `requirements.txt` (`psycopg2-binary` for PostgreSQL)
- Node deps: `npm install` (tailwindcss, alpinejs, htmx.org, flowbite, concurrently)

## Workflow
- **Start application**: `python manage.py runserver 0.0.0.0:5000` — port 5000, webview

## Deployment
- Configured for Render: `gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 --timeout=120 attendance_system.wsgi`
- Required env vars in production: `DJANGO_SECRET_KEY`, `DATABASE_URL`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`
- Optional: `CLOUDINARY_URL` (media storage), `BREVO_API_KEY` (email), `REDIS_URL` (Celery)

## Replit-Specific Notes
- `ALLOWED_HOSTS = ['*']` in DEBUG mode for Replit proxy compatibility
- `CSRF_TRUSTED_ORIGINS` includes `*.replit.dev`, `*.repl.co`, `*.replit.app` in DEBUG mode
- Admin panel at `/exodus-manage/` (obfuscated from `/admin/`)
- Health check endpoint at `/health/`
- API docs (Swagger) at `/api/docs/`

## UI Audit Status (Complete — 6 batches pushed)
All templates have been upgraded to the design system. Key improvements:
- Batch 1–3: Dashboard, nav, sidebar, attendance pages, courses, profile, reports
- Batch 4: Register (2-col grid), take attendance (full-width), student detail (pill-row cards)
- Batch 5: All delete confirmations (glassy danger cards), lecturer detail, 2FA pages, pagination, upload pages, progress card (Bootstrap → Tailwind), partials
- Batch 6: Brand colour consistency — list partials (student/lecturer rows + content), base skip link, login links, profile checkbox
