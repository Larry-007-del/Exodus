#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting Deployment Tasks..."

# 1. Apply Database Migrations (Fixes missing tables)
echo "✅ Applying Database Migrations..."
python manage.py migrate --no-input

# 2. Create Superuser (Fixes login)
# This uses the environment variables you set in the Dashboard
echo "✅ Creating Superuser..."
python manage.py createsuperuser --no-input || echo "⚠️ Superuser might already exist or variables are missing."

# 3. Start the Server
echo "🚀 Starting Gunicorn..."
exec gunicorn attendance_system.wsgi:application
