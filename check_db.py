import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "shop.db"


def show_query(cursor, title, query, params=()):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    if not rows:
        print("Нет данных")
        return
    for row in rows:
        print(row)
    print(f"Строк в результате: {len(rows)}")


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    show_query(cursor, "Все записи о продажах", "SELECT * FROM sales")

    show_query(
        cursor,
        "Задание 3. Товары дороже 20 000 тенге",
        "SELECT id, product, category, price, quantity, sale_date "
        "FROM sales WHERE price > 20000 ORDER BY price DESC",
    )

    show_query(
        cursor,
        "Задание 4. Товары категории «Техника»",
        "SELECT id, product, category, price, quantity, sale_date "
        "FROM sales WHERE category = ? ORDER BY price DESC",
        ("Техника",),
    )

    show_query(
        cursor,
        "Задание 5. Сортировка по цене (от дорогой к дешёвой)",
        "SELECT id, product, price FROM sales ORDER BY price DESC",
    )

    show_query(
        cursor,
        "Задание 6. Количество записей в таблице",
        "SELECT COUNT(*) AS total_records FROM sales",
    )

    show_query(
        cursor,
        "Дополнительно: количество записей по категориям",
        "SELECT category, COUNT(*) AS records, SUM(quantity) AS units "
        "FROM sales GROUP BY category ORDER BY records DESC",
    )

    conn.close()


if __name__ == "__main__":
    main()
