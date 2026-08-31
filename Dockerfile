FROM python:3.12-slim

# System configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Runtime OS dependencies:
#   - libpq5           -> PostgreSQL client library (for psycopg2-binary)
#   - gettext          -> Django compilemessages / translations
#   - curl             -> container healthcheck
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        gettext \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies (cached layer)
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Application source
COPY . .

# Entrypoint handles DB wait, migrations, static and CSV import
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh \
    && chmod +x /usr/local/bin/entrypoint.sh

# Docker-specific configuration (DB host = db, bind 0.0.0.0)
COPY docker/conf.ini /app/src/conf.ini

WORKDIR /app/src

EXPOSE 8077

ENTRYPOINT ["entrypoint.sh"]
CMD ["python", "web.py"]
