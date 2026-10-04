#!/bin/sh
set -eu

echo "Starting ElectroMarket entrypoint..."
uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput

# Ensure product images exist on ephemeral Fly disks (paths live in Supabase).
if [ ! -d /app/media/products ] || [ -z "$(ls -A /app/media/products 2>/dev/null || true)" ]; then
  echo "No product media found; seeding images..."
  uv run python manage.py seed_smartphones --force || true
fi

exec uv run gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8080}" \
  --workers 2 \
  --timeout 120
