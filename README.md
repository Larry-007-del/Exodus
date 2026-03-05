# Exodus — University Attendance System

A full-stack Django web application for managing university attendance with GPS-based verification, QR code check-ins, role-based dashboards, and real-time notifications.

[![CI](https://github.com/Larry-007-del/Exodus/actions/workflows/ci.yml/badge.svg)](https://github.com/Larry-007-del/Exodus/actions/workflows/ci.yml)

---

## Features

- **GPS-Based Attendance** — Students submit their location; the system verifies they are within range of the lecturer
- **QR Code Check-In** — Lecturers generate time-limited attendance tokens with QR codes
- **Role-Based Access** — Admin, Lecturer, and Student roles with tailored dashboards and permissions
- **Real-Time Notifications** — Email and SMS alerts for attendance sessions (configurable per-student)
- **Two-Factor Authentication** — Optional TOTP-based 2FA for lecturers and students
- **Reports & Analytics** — Attendance trends, course statistics, CSV/Excel exports
- **REST API** — Full DRF-powered API with Swagger/OpenAPI documentation
- **Responsive UI** — Tailwind CSS + Alpine.js + HTMX for a modern, interactive frontend

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.0, Django REST Framework |
| Frontend | Tailwind CSS 3.4, Alpine.js 3.15, HTMX 2.0, Flowbite |
| Database | SQLite (dev), PostgreSQL (production) |
| Auth | Token authentication, session auth, TOTP 2FA |
| Media | Cloudinary (production), local storage (dev) |
| Static Files | WhiteNoise, PostCSS/Tailwind build pipeline |
| Deployment | Render (Gunicorn), GitHub Actions CI |
| Monitoring | Sentry error tracking |

---

## Project Structure

```
attendance_system_master/
├── attendance/              # Core app — models, REST API, serializers
│   ├── models.py            # Lecturer, Student, Course, Attendance, AttendanceToken
│   ├── views.py             # DRF ViewSets and API views
│   ├── serializers.py       # REST serializers with schema annotations
│   ├── urls.py              # API URL routing
│   └── tests.py             # 81 API/model/serializer tests
├── frontend/                # Web UI app — server-rendered templates
│   ├── views.py             # All page views (dashboard, CRUD, reports)
│   ├── urls.py              # Frontend URL routing
│   └── tests.py             # 87 view tests
├── attendance_system/       # Django project settings
│   └── settings.py          # Configuration (security, DB, email, etc.)
├── templates/               # Django templates (Jinja-style)
│   ├── base.html            # Main layout with sidebar, nav, footer
│   ├── dashboard.html       # Role-aware dashboard
│   ├── attendance/          # Attendance management pages
│   ├── courses/             # Course CRUD pages
│   ├── students/            # Student management pages
│   ├── lecturers/           # Lecturer management pages
│   ├── reports/             # Analytics and export pages
│   └── errors/              # Custom 404/500 error pages
├── static/                  # Built frontend assets
│   ├── css/styles.css       # Compiled Tailwind CSS
│   └── js/                  # Alpine.js, HTMX, Flowbite (local)
├── .github/workflows/       # CI pipeline
│   └── ci.yml               # GitHub Actions — test on every push/PR
├── build.sh                 # Render build script
├── entrypoint.sh            # Render start script
├── render.yaml              # Render deployment config
├── package.json             # Node.js — Tailwind/PostCSS build
├── tailwind.config.js       # Tailwind configuration
└── requirements.txt         # Python dependencies
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+ (for frontend asset builds)
- Git

### Local Setup

```bash
# Clone the repository
git clone https://github.com/Larry-007-del/Exodus.git
cd Exodus/attendance_system_master

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies & build frontend assets
npm install
npm run build

# Apply database migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

Visit `http://localhost:8000` — you'll be redirected to the login page.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | insecure dev key | Secret key for production |
| `DJANGO_DEBUG` | `True` | Set `False` in production |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated allowed hosts |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | PostgreSQL URL for production |
| `CLOUDINARY_CLOUD_NAME` | — | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | — | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | — | Cloudinary API secret |
| `EMAIL_HOST_USER` | — | SMTP email address |
| `EMAIL_HOST_PASSWORD` | — | SMTP app password |
| `SENTRY_DSN` | — | Sentry error tracking DSN |
| `TWILIO_ACCOUNT_SID` | — | Twilio SMS SID |
| `TWILIO_AUTH_TOKEN` | — | Twilio SMS auth token |
| `TWILIO_PHONE_NUMBER` | — | Twilio sender number |

---

## API Reference

The API is served under `/api/` with Swagger docs at `/api/docs/`.

### Authentication

All API endpoints require token authentication. Obtain a token via:

```
POST /api/login/student/    { username, password, student_id }
POST /api/login/staff/      { username, password, staff_id }
```

Include the token in subsequent requests:

```
Authorization: Token <your-token>
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lecturers/` | List all lecturers |
| GET | `/api/students/` | List students (filtered by role) |
| GET | `/api/courses/` | List all courses |
| GET | `/api/attendances/` | List attendance records |
| GET | `/api/attendance-tokens/` | List attendance tokens |
| GET | `/api/lecturers/my-courses/` | Lecturer's own courses |
| POST | `/api/submit-location/` | Student submits GPS for check-in |
| POST | `/api/logout/` | Invalidate auth token |
| GET | `/api/student-attendance-history/` | Student's attendance history |
| GET | `/api/lecturer-attendance-history/` | Lecturer's attendance history |
| POST | `/api/lecturer-location/` | Get lecturer coordinates by token |

Full interactive docs: `/api/docs/` (Swagger UI)

---

## Testing

The project has **168 tests** covering models, API endpoints, serializers, and all frontend views.

```bash
# Run all tests
python manage.py test

# Run with verbose output
python manage.py test --verbosity=2

# Run specific app tests
python manage.py test attendance
python manage.py test frontend
```

Tests run automatically on every push via GitHub Actions CI.

---

## Deployment (Render)

The project is configured for [Render](https://render.com) deployment:

1. Connect your GitHub repo to Render
2. Set environment variables (see table above) — at minimum `DJANGO_SECRET_KEY` and `DATABASE_URL`
3. Render will use `build.sh` (install deps, build assets, migrate) and `entrypoint.sh` (collectstatic, start Gunicorn)

The deployment includes:
- **Gunicorn** with 2 workers bound to `0.0.0.0:${PORT}`
- **WhiteNoise** for static file serving
- **PostgreSQL** via `DATABASE_URL`
- **HSTS**, secure cookies, and SSL redirect in production
- **Sentry** error tracking (if `SENTRY_DSN` is set)

---

## Security

Production mode automatically enables:

- HTTPS redirect (`SECURE_SSL_REDIRECT`)
- Secure session and CSRF cookies
- HSTS headers (1 year, include subdomains, preload)
- XSS and content-type sniffing protection
- API rate limiting (10/min anonymous, 1000/day authenticated)

---

## License

This project is licensed under the ISC License.
