import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "shop.db")


async def init_db():
    """Создаёт таблицу и наполняет тестовыми данными при первом запуске."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                category    TEXT,
                description TEXT,
                price       REAL NOT NULL,
                image_url   TEXT,
                barcode     TEXT,
                in_stock    INTEGER DEFAULT 1,
                created_at  TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.commit()

        # Наполняем только если таблица пустая
        cursor = await db.execute("SELECT COUNT(*) FROM products")
        (count,) = await cursor.fetchone()
        if count == 0:
            await db.executemany(
                """INSERT INTO products
                   (name, category, description, price, barcode)
                   VALUES (?, ?, ?, ?, ?)""",
                [
                    ("Coca-Cola 1L",         "Напитки",  "Газированный напиток Coca-Cola 1 литр",       450,  "4870200013834"),
                    ("Lay's Сметана 150г",   "Снеки",    "Чипсы картофельные со вкусом сметаны",        350,  "4823063107456"),
                    ("Sprite 0.5L",          "Напитки",  "Газированный напиток Sprite 500 мл",           320,  "5449000014238"),
                    ("Шоколад Milka 90г",    "Сладости", "Молочный шоколад с альпийским молоком",        520,  "7622300441937"),
                    ("Чай Lipton 25 пак",    "Продукты", "Чай чёрный в пакетиках",                       680,  "8712100851637"),
                    ("Red Bull 250мл",       "Напитки",  "Энергетический напиток Red Bull",              750,  "9002490100070"),
                    ("Snickers 50г",         "Сладости", "Шоколадный батончик Snickers",                 280,  "4600831012501"),
                    ("Orbit Spearmint",      "Прочее",   "Жевательная резинка Orbit мята",               250,  "4009900476003"),
                    ("Вода Bonaqua 1L",      "Напитки",  "Питьевая вода без газа",                       200,  "4870200011502"),
                    ("Pringles Original",    "Снеки",    "Чипсы Pringles в тубе оригинальные",           890,  "0038000845598"),
                ],
            )
            await db.commit()


async def search_products(queries: list[str]) -> list[dict]:
    """
    LIKE-поиск по имени и описанию.
    Для каждого запроса берём топ-2 результата, дедуплицируем по id.
    """
    results = []
    seen_ids: set[int] = set()

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row  # доступ по имени колонки

        for q in queries:
            pattern = f"%{q}%"
            cursor = await db.execute(
                """
                SELECT id, name, category, description, price, image_url, barcode
                FROM products
                WHERE in_stock = 1
                  AND (name LIKE ? OR description LIKE ?)
                LIMIT 2
                """,
                (pattern, pattern),
            )
            rows = await cursor.fetchall()
            for row in rows:
                if row["id"] not in seen_ids:
                    seen_ids.add(row["id"])
                    results.append(dict(row))

    return results


async def get_all_products() -> list[dict]:
    """Возвращает все товары из базы данных."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row  # доступ по имени колонки

        cursor = await db.execute(
            """
            SELECT id, name, category, description, price, image_url, barcode, in_stock, created_at
            FROM products
            ORDER BY name
            """
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]