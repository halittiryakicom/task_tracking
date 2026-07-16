#!/bin/bash
set -e

echo "=== İş Takip Django — Container EntryPoint ==="

# Ensure data directory exists and is writable
mkdir -p /app/data

# Apply database migrations
echo "→ Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "→ Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if DJANGO_SUPERUSER_* env vars are set
if [[ -n "$DJANGO_SUPERUSER_USERNAME" && -n "$DJANGO_SUPERUSER_PASSWORD" && -n "$DJANGO_SUPERUSER_EMAIL" ]]; then
    echo "→ Creating superuser..."
    python manage.py createsuperuser \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL" \
        --noinput 2>/dev/null || echo "  Superuser already exists, skipping."
fi

# Determine server mode
if [[ "$DJANGO_DEBUG" = "True" || "$DJANGO_DEBUG" = "true" || "$DJANGO_DEBUG" = "1" ]]; then
    echo "→ Starting development server (DEBUG=$DJANGO_DEBUG)..."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "→ Starting production server with Gunicorn..."
    exec gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers "${GUNICORN_WORKERS:-4}" \
        --timeout "${GUNICORN_TIMEOUT:-120}" \
        --access-logfile - \
        --error-logfile -
fi
