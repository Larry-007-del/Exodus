#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting Deployment Tasks..."

# --- NEW STEP: Fixes the 500 Error ---
echo "🎨 Collecting Static Files..."
python manage.py collectstatic --no-input --clear
# -------------------------------------

echo "📦 Applying Database Migrations..."
python manage.py migrate --no-input

echo "👤 Creating Superuser..."
python manage.py createsuperuser --no-input || echo "⚠️ Superuser creation skipped (already exists or missing variables)."

echo "🔥 Starting Gunicorn..."
exec gunicorn attendance_system.wsgi:application
