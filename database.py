import asyncpg
from datetime import datetime
from config import DATABASE_URL

_pool: asyncpg.Pool | None = None


async def init_db():
    """Postgres pool ochadi va jadvallarni (agar bo'lmasa) yaratadi."""
    global _pool
    _pool = await asyncpg.create_pool(dsn=DATABASE_URL)
    async with _pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            full_name TEXT,
            birth_year INTEGER,
            phone TEXT,
            workplace TEXT,
            income BIGINT,
            family_status TEXT,
            address TEXT,
            house_type TEXT,
            phone_years INTEGER,
            guarantor TEXT,
            product TEXT,
            other_credit TEXT,
            other_credit_amount BIGINT,
            score INTEGER,
            status TEXT DEFAULT 'kutilmoqda',
            debt BIGINT DEFAULT 0,
            created_at TEXT
        )
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            filial_key TEXT,
            filial_name TEXT,
            amount BIGINT,
            status TEXT DEFAULT 'kutilmoqda',
            created_at TEXT
        )
        """)


async def close_db():
    """Botni to'xtatishda pool'ni yopish uchun (main.py da chaqiriladi)."""
    if _pool:
        await _pool.close()


async def save_application(data: dict, score: int):
    async with _pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users (
            user_id, full_name, birth_year, phone, workplace, income,
            family_status, address, house_type, phone_years, guarantor,
            product, other_credit, other_credit_amount, score, status, debt, created_at
        ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18)
        ON CONFLICT (user_id) DO UPDATE SET
            full_name=EXCLUDED.full_name,
            birth_year=EXCLUDED.birth_year,
            phone=EXCLUDED.phone,
            workplace=EXCLUDED.workplace,
            income=EXCLUDED.income,
            family_status=EXCLUDED.family_status,
            address=EXCLUDED.address,
            house_type=EXCLUDED.house_type,
            phone_years=EXCLUDED.phone_years,
            guarantor=EXCLUDED.guarantor,
            product=EXCLUDED.product,
            other_credit=EXCLUDED.other_credit,
            other_credit_amount=EXCLUDED.other_credit_amount,
            score=EXCLUDED.score,
            status='kutilmoqda',
            created_at=EXCLUDED.created_at
        """,
            data["user_id"], data["full_name"], data["birth_year"], data["phone"],
            data["workplace"], data["income"], data["family_status"], data["address"],
            data["house_type"], data["phone_years"], data["guarantor"], data["product"],
            data["other_credit"], data.get("other_credit_amount", 0), score,
            "kutilmoqda", 0, datetime.now().strftime("%Y-%m-%d %H:%M")
        )


async def get_user(user_id: int):
    async with _pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
        return dict(row) if row else None


async def set_status(user_id: int, status: str):
    async with _pool.acquire() as conn:
        await conn.execute("UPDATE users SET status=$1 WHERE user_id=$2", status, user_id)


async def set_debt(user_id: int, amount: int):
    async with _pool.acquire() as conn:
        await conn.execute("UPDATE users SET debt=$1 WHERE user_id=$2", amount, user_id)


async def decrease_debt(user_id: int, amount: int):
    user = await get_user(user_id)
    new_debt = max(0, (user["debt"] or 0) - amount)
    await set_debt(user_id, new_debt)
    return new_debt


async def create_payment(user_id: int, filial_key: str, filial_name: str, amount: int):
    async with _pool.acquire() as conn:
        row = await conn.fetchrow("""
        INSERT INTO payments (user_id, filial_key, filial_name, amount, status, created_at)
        VALUES ($1,$2,$3,$4,$5,$6)
        RETURNING id
        """, user_id, filial_key, filial_name, amount, "kutilmoqda",
             datetime.now().strftime("%Y-%m-%d %H:%M"))
        return row["id"]


async def get_payment(payment_id: int):
    async with _pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM payments WHERE id=$1", payment_id)
        return dict(row) if row else None


async def set_payment_status(payment_id: int, status: str):
    async with _pool.acquire() as conn:
        await conn.execute("UPDATE payments SET status=$1 WHERE id=$2", status, payment_id)