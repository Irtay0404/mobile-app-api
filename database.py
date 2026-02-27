import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=2,
            max_size=10,
        )
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def search_products(queries: list[str]) -> list[dict]:
    """Fuzzy-поиск товаров по списку запросов из OpenAI."""
    pool = await get_pool()
    results = []
    seen_ids = set()

    for q in queries:
        rows = await pool.fetch(
            """
            SELECT id, name, category, description, price, image_url, barcode
            FROM products
            WHERE in_stock = TRUE
              AND (
                LOWER(name) LIKE LOWER($1)
                OR name % $2
                OR LOWER(description) LIKE LOWER($1)
              )
            ORDER BY similarity(name, $2) DESC
            LIMIT 3
            """,
            f"%{q}%",
            q,
        )
        for row in rows:
            if row["id"] not in seen_ids:
                seen_ids.add(row["id"])
                results.append(dict(row))

    return results