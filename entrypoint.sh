#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# build.sh handles collectstatic, but migrations must also run at startup
# in case the build step ran before DATABASE_URL was available.

echo "🔄 Running migrations..."
python manage.py migrate --no-input

# collectstatic already ran in build.sh — skip it here to keep startup fast
# Create superuser if env vars are set (skip if user already exists)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  echo "👤 Ensuring superuser exists..."
  python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
import os
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=os.environ.get('DJANGO_SUPERUSER_EMAIL', ''),
        password=os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    )
    print(f'Superuser \"{username}\" created.')
else:
    print(f'Superuser \"{username}\" already exists, skipping.')
"
fi
echo "�🔥 Starting Gunicorn..."
exec gunicorn attendance_system.wsgi:application \
    --bind "0.0.0.0:${PORT:-10000}" \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
