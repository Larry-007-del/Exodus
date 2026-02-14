#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Dependencies
pip install -r requirements.txt

# 2. Collect Static Files (CSS/JS)
python manage.py collectstatic --no-input

# 3. Apply Database Migrations
python manage.py migrate

# 4. Create Superuser (Automatically)
# This command checks environment variables and creates the user if they don't exist
python manage.py createsuperuser --no-input --email "$DJANGO_SUPERUSER_EMAIL" || true
