-- ────────────────────────────────────────────────────────────────────────────
-- Database initialisation script
-- Runs once on first PostgreSQL container start (docker-entrypoint-initdb.d)
-- ────────────────────────────────────────────────────────────────────────────

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Schema
CREATE SCHEMA IF NOT EXISTS app AUTHORIZATION app_user;

-- Application user with limited grants
GRANT CONNECT ON DATABASE fastapi_app TO app_user;
GRANT USAGE ON SCHEMA app TO app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA app TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA app TO app_user;

-- ── Example: Users table ──────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS app.users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) NOT NULL UNIQUE,
    full_name   VARCHAR(255),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON app.users (email);
CREATE INDEX idx_users_created_at ON app.users (created_at);

-- ── Example: Items table ───────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS app.items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    price       NUMERIC(10, 2) NOT NULL DEFAULT 0,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_items_user_id ON app.items (user_id);
CREATE INDEX idx_items_created_at ON app.items (created_at);

-- ── Update trigger helper ──────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION app.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to tables
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON app.users
    FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();

CREATE TRIGGER trg_items_updated_at
    BEFORE UPDATE ON app.items
    FOR EACH ROW EXECUTE FUNCTION app.set_updated_at();
