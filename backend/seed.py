"""Создание первого садика и суперадмина."""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

RAW_URL = os.getenv("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")

KG_NAME = "Садик Солнышко"
ADMIN_EMAIL = "admin@kindermanager.kz"
ADMIN_PASSWORD = "admin1234"
ADMIN_NAME = "Daniil (Администратор)"


async def main():
    conn = await asyncpg.connect(RAW_URL)
    try:
        # Create kindergarten
        kg = await conn.fetchrow(
            "INSERT INTO kindergartens (name) VALUES ($1) "
            "ON CONFLICT DO NOTHING RETURNING id, name",
            KG_NAME
        )
        if kg:
            kg_id = kg["id"]
            print(f"✅ Садик создан: {KG_NAME} (id: {kg_id})")
        else:
            kg = await conn.fetchrow("SELECT id FROM kindergartens WHERE name=$1", KG_NAME)
            kg_id = kg["id"]
            print(f"ℹ️  Садик уже существует (id: {kg_id})")

        # Create superadmin
        existing = await conn.fetchrow("SELECT id FROM users WHERE email=$1", ADMIN_EMAIL)
        if existing:
            print(f"ℹ️  Суперадмин уже существует ({ADMIN_EMAIL})")
        else:
            pw_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
            user = await conn.fetchrow(
                """INSERT INTO users (kindergarten_id, role, full_name, email, password_hash)
                   VALUES ($1, 'superadmin', $2, $3, $4) RETURNING id""",
                kg_id, ADMIN_NAME, ADMIN_EMAIL, pw_hash
            )
            print(f"✅ Суперадмин создан!")

        print(f"\n📋 Данные для входа в веб-панель:")
        print(f"   Email:    {ADMIN_EMAIL}")
        print(f"   Пароль:   {ADMIN_PASSWORD}")
        print(f"   Садик ID: {kg_id}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
