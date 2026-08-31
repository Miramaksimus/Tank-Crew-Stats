-- Extensions required by IL-2 Stats (django.contrib.postgres / hstore fields).
-- Runs once, as superuser, against POSTGRES_DB during first container init.
CREATE EXTENSION IF NOT EXISTS hstore;
CREATE EXTENSION IF NOT EXISTS citext;
