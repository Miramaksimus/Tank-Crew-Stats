#!/usr/bin/env bash
set -e

cd /app/src

# --- Persist Django SECRET_KEY across restarts (optional) ---------------------
# If SECRET_KEY is provided via env and no key file exists yet, write it so the
# app doesn't regenerate a new one on every container start (which would
# invalidate all existing sessions).
if [ -n "${SECRET_KEY:-}" ] && [ ! -f SECRET_KEY ]; then
    printf '%s' "${SECRET_KEY}" > SECRET_KEY
fi

# --- Wait for PostgreSQL ------------------------------------------------------
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-il2_stats}"
DB_USER="${DB_USER:-il2_stats}"
DB_PASSWORD="${DB_PASSWORD:-il2_stats}"

echo "Waiting for database ${DB_HOST}:${DB_PORT} ..."
python - <<PY
import os, sys, time
import psycopg2

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "5432"))
name = os.environ.get("DB_NAME", "il2_stats")
user = os.environ.get("DB_USER", "il2_stats")
password = os.environ.get("DB_PASSWORD", "il2_stats")

for attempt in range(60):
    try:
        psycopg2.connect(host=host, port=port, dbname=name, user=user, password=password).close()
        print("Database is ready.")
        sys.exit(0)
    except Exception as exc:
        print(f"  db not ready ({attempt + 1}/60): {exc}")
        time.sleep(2)
print("Database did not become ready in time.", file=sys.stderr)
sys.exit(1)
PY

# --- One-time / idempotent setup (only for the web service) ------------------
# The parser service sets RUN_SETUP=0 to skip; the web service runs migrations,
# collects static files and imports game-object CSV data (all idempotent).
if [ "${RUN_SETUP:-1}" = "1" ]; then
    echo "Applying database migrations ..."
    python manage.py migrate --noinput

    echo "Collecting static files ..."
    python manage.py collectstatic --noinput

    echo "Importing game object CSV data ..."
    python manage.py import_csv_data

    # Create an admin user if credentials are supplied and it doesn't exist yet.
    if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
        echo "Ensuring superuser '${DJANGO_SUPERUSER_USERNAME}' exists ..."
        python manage.py createsuperuser --noinput \
            --username "${DJANGO_SUPERUSER_USERNAME}" \
            --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" || true
    fi
fi

exec "$@"
