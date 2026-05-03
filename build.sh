#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Python Dependencies
pip install -r requirements.txt

# 2. Install Node.js Dependencies & Build Frontend Assets
# Failures here are non-fatal — static source files are already committed to git
if command -v node &> /dev/null; then
  npm ci --production=false && npm run build || echo "[WARNING] Node.js build step failed — using committed static assets"
fi

# 3. Collect Static Files (CSS/JS)
python manage.py collectstatic --no-input

# Note: Database migrations are handled in entrypoint.sh at runtime,
# because DATABASE_URL may not be available during the build step.
