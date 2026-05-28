"""Прямой запуск миграций через asyncpg (обход проблемы greenlet на Python 3.14)."""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

RAW_URL = os.getenv("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")

SQL = """
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS kindergartens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    city        VARCHAR(100),
    address     TEXT,
    phone       VARCHAR(30),
    created_at  TIMESTAMP DEFAULT NOW(),
    is_active   BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS users (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kindergarten_id     UUID REFERENCES kindergartens(id),
    role                VARCHAR(20) NOT NULL,
    full_name           VARCHAR(255) NOT NULL,
    phone               VARCHAR(30),
    email               VARCHAR(255) UNIQUE,
    password_hash       VARCHAR(255),
    telegram_id         BIGINT UNIQUE,
    telegram_username   VARCHAR(100),
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS groups (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kindergarten_id UUID REFERENCES kindergartens(id),
    name            VARCHAR(100) NOT NULL,
    age_from        INTEGER,
    age_to          INTEGER,
    teacher_id      UUID REFERENCES users(id),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS children (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kindergarten_id UUID REFERENCES kindergartens(id),
    group_id        UUID REFERENCES groups(id),
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    birth_date      DATE NOT NULL,
    gender          VARCHAR(10),
    photo_url       TEXT,
    allergies       TEXT,
    medical_notes   TEXT,
    created_at      TIMESTAMP DEFAULT NOW(),
    is_active       BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS parent_child (
    parent_id   UUID REFERENCES users(id),
    child_id    UUID REFERENCES children(id),
    relation    VARCHAR(30),
    PRIMARY KEY (parent_id, child_id)
);

CREATE TABLE IF NOT EXISTS attendance (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id    UUID REFERENCES children(id),
    date        DATE NOT NULL,
    status      VARCHAR(20) NOT NULL,
    note        TEXT,
    marked_by   UUID REFERENCES users(id),
    marked_at   TIMESTAMP DEFAULT NOW(),
    UNIQUE(child_id, date)
);

CREATE TABLE IF NOT EXISTS schedule (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id    UUID REFERENCES groups(id),
    day_of_week INTEGER NOT NULL,
    time_start  TIME NOT NULL,
    time_end    TIME NOT NULL,
    subject     VARCHAR(100) NOT NULL,
    teacher_id  UUID REFERENCES users(id),
    room        VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS menu (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kg_id       UUID REFERENCES kindergartens(id),
    date        DATE NOT NULL,
    meal_type   VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    calories    INTEGER
);

CREATE TABLE IF NOT EXISTS posts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kg_id       UUID REFERENCES kindergartens(id),
    group_id    UUID REFERENCES groups(id),
    author_id   UUID REFERENCES users(id),
    type        VARCHAR(20) NOT NULL,
    title       VARCHAR(255),
    content     TEXT,
    media_urls  TEXT[],
    created_at  TIMESTAMP DEFAULT NOW(),
    is_sent     BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS medical_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id        UUID REFERENCES children(id),
    record_type     VARCHAR(30),
    title           VARCHAR(255),
    description     TEXT,
    date            DATE,
    next_date       DATE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS documents (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id    UUID REFERENCES children(id),
    kg_id       UUID REFERENCES kindergartens(id),
    type        VARCHAR(50),
    title       VARCHAR(255),
    file_url    TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS telegram_sessions (
    telegram_id BIGINT PRIMARY KEY,
    user_id     UUID REFERENCES users(id),
    state       VARCHAR(100),
    state_data  JSONB,
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS invite_codes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(10) NOT NULL UNIQUE,
    kg_id       UUID REFERENCES kindergartens(id),
    role        VARCHAR(20) NOT NULL,
    user_id     UUID REFERENCES users(id),
    is_used     BOOLEAN DEFAULT FALSE,
    expires_at  TIMESTAMP,
    created_at  TIMESTAMP DEFAULT NOW()
);
"""


async def main():
    print(f"Connecting to Supabase...")
    conn = await asyncpg.connect(RAW_URL)
    try:
        await conn.execute(SQL)
        print("✅ All tables created successfully!")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
