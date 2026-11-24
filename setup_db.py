import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "shop.db"

SALES = [
    ("Ноутбук", "Техника", 320000, 2, "2026-11-01"),
    ("Мышь", "Аксессуары", 6500, 8, "2026-11-01"),
    ("Монитор", "Техника", 95000, 3, "2026-11-02"),
    ("Клавиатура", "Периферия", 14000, 5, "2026-11-02"),
    ("Наушники", "Аудио", 23000, 4, "2026-11-03"),
    ("Смартфон", "Техника", 180000, 3, "2026-11-03"),
    ("SSD 1TB", "Хранение данных", 42000, 6, "2026-11-03"),
    ("Веб-камера", "Периферия", 18500, 4, "2026-11-04"),
    ("Колонка", "Аудио", 27000, 3, "2026-11-04"),
    ("Флешка 64GB", "Хранение данных", 4500, 12, "2026-11-04"),
    ("Планшет", "Техника", 145000, 2, "2026-11-05"),
    ("Коврик для мыши", "Аксессуары", 3500, 10, "2026-11-05"),
    ("Микрофон", "Аудио", 39000, 2, "2026-11-05"),
    ("Внешний диск 2TB", "Хранение данных", 56000, 4, "2026-11-06"),
    ("Ноутбук", "Техника", 320000, 1, "2026-11-06"),
    ("Мышь", "Аксессуары", 6500, 5, "2026-11-06"),
    ("Монитор", "Техника", 95000, 2, "2026-11-07"),
    ("Клавиатура", "Периферия", 14000, 7, "2026-11-07"),
    ("Наушники", "Аудио", 23000, 3, "2026-11-07"),
    ("SSD 1TB", "Хранение данных", 42000, 5, "2026-11-08"),
    ("Смартфон", "Техника", 180000, 2, "2026-11-08"),
    ("Веб-камера", "Периферия", 18500, 3, "2026-11-08"),
    ("Power Bank", "Аксессуары", 9500, 6, "2026-11-09"),
    ("Колонка", "Аудио", 27000, 2, "2026-11-09"),
    ("Внешний диск 2TB", "Хранение данных", 56000, 3, "2026-11-09"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            price INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            sale_date TEXT NOT NULL
        )
        """
    )

    cursor.execute("SELECT COUNT(*) FROM sales")
    existing = cursor.fetchone()[0]

    if existing == 0:
        cursor.executemany(
            """
            INSERT INTO sales
            (product, category, price, quantity, sale_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            SALES,
        )
        conn.commit()
        print(f"База данных создана! Добавлено записей: {len(SALES)}")
    else:
        print(f"Таблица sales уже содержит {existing} записей. Повторная вставка пропущена.")

    cursor.execute("SELECT COUNT(DISTINCT category) FROM sales")
    categories = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM sales")
    total = cursor.fetchone()[0]

    print(f"Файл базы данных: {DB_PATH}")
    print(f"Всего записей: {total}")
    print(f"Категорий: {categories}")

    conn.close()


if __name__ == "__main__":
    main()
