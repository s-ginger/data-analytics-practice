import shutil
import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "shop.db"
CHARTS_DIR = BASE_DIR / "charts"


def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    df["revenue"] = df["price"] * df["quantity"]
    return df


def check_quality(df):
    print("\n" + "=" * 60)
    print("ПРОВЕРКА КАЧЕСТВА ДАННЫХ")
    print("=" * 60)

    print("\nПропуски по столбцам:")
    print(df.isna().sum())

    print(f"\nПолных дубликатов строк: {df.duplicated().sum()}")

    columns = ["product", "category", "price", "quantity", "sale_date"]
    print(f"Дубликатов без учёта id: {df.duplicated(subset=columns).sum()}")

    print(f"\nСредняя цена: {df['price'].mean():,.2f} тенге")
    print(f"Медианная цена: {df['price'].median():,.2f} тенге")
    print(f"Минимальная цена: {df['price'].min():,.0f} тенге")
    print(f"Максимальная цена: {df['price'].max():,.0f} тенге")


def investigate_outlier(df):
    print("\n" + "=" * 60)
    print("ИССЛЕДОВАНИЕ ВЫБРОСА")
    print("=" * 60)

    backup_path = BASE_DIR / "shop_backup.db"
    shutil.copyfile(DB_PATH, backup_path)
    print(f"Создана резервная копия базы: {backup_path.name}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    test_id = None

    try:
        before_mean = df["price"].mean()
        before_median = df["price"].median()

        cursor.execute(
            """
            INSERT INTO sales (product, category, price, quantity, sale_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("Тестовый товар", "Техника", 15000000, 1, "2026-11-10"),
        )
        test_id = cursor.lastrowid
        conn.commit()

        after = pd.read_sql_query("SELECT price FROM sales", conn)
        after_mean = after["price"].mean()
        after_median = after["price"].median()

        print(f"Добавлена тестовая запись id={test_id} с ценой 15 000 000 тенге")
        print(f"Средняя цена до:    {before_mean:,.2f} тенге")
        print(f"Средняя цена после: {after_mean:,.2f} тенге")
        print(f"Медиана до:         {before_median:,.2f} тенге")
        print(f"Медиана после:      {after_median:,.2f} тенге")
        print(
            "Вывод: выброс сильно увеличил среднее значение, "
            "но почти не повлиял на медиану."
        )
    finally:
        if test_id is not None:
            cursor.execute("DELETE FROM sales WHERE id = ?", (test_id,))
            conn.commit()
        cursor.execute("SELECT COUNT(*) FROM sales")
        remaining = cursor.fetchone()[0]
        conn.close()
        backup_path.unlink(missing_ok=True)
        print(f"Тестовая запись удалена. Записей в базе: {remaining}")


def build_charts(df):
    CHARTS_DIR.mkdir(exist_ok=True)

    products = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    categories = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
    units_by_product = df.groupby("product")["quantity"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    products.plot(kind="bar", ax=ax, color="#3b82f6")
    ax.set_title("Выручка по товарам")
    ax.set_xlabel("Товар")
    ax.set_ylabel("Выручка, тенге")
    ax.tick_params(axis="x", rotation=45)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    fig.tight_layout()
    products_path = CHARTS_DIR / "products.png"
    fig.savefig(products_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 8))
    categories.plot(kind="pie", ax=ax, autopct="%1.1f%%", startangle=90)
    ax.set_title("Доля категорий в выручке")
    ax.set_ylabel("")
    fig.tight_layout()
    categories_path = CHARTS_DIR / "categories.png"
    fig.savefig(categories_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 6))
    units_by_product.plot(kind="bar", ax=ax, color="#10b981")
    ax.set_title("Количество проданных единиц по товарам")
    ax.set_xlabel("Товар")
    ax.set_ylabel("Количество, шт.")
    ax.tick_params(axis="x", rotation=45)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    fig.tight_layout()
    quantity_path = CHARTS_DIR / "quantity.png"
    fig.savefig(quantity_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    daily = df.groupby("sale_date")["revenue"].sum().sort_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    daily.plot(kind="line", marker="o", ax=ax, color="#ef4444")
    ax.set_title("Динамика выручки по датам")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Выручка, тенге")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    daily_path = CHARTS_DIR / "daily.png"
    fig.savefig(daily_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    daily_units = df.groupby("sale_date")["quantity"].sum().sort_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    daily_units.plot(kind="line", marker="s", ax=ax, color="#8b5cf6")
    ax.set_title("Количество проданных товаров по дням")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Количество, шт.")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    daily_quantity_path = CHARTS_DIR / "daily_quantity.png"
    fig.savefig(daily_quantity_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print("\nСохранённые графики:")
    for path in (
        products_path,
        categories_path,
        quantity_path,
        daily_path,
        daily_quantity_path,
    ):
        print(f"  {path.relative_to(BASE_DIR)}")

    return products, categories, daily, daily_units


def main():
    if not DB_PATH.exists():
        print("База данных не найдена. Сначала запустите setup_db.py")
        return

    df = load_data()

    print("Первые записи:")
    print(df.head())
    print("\nВыручка по записям:")
    print(df[["product", "revenue"]])

    total = df["revenue"].sum()
    total_units = df["quantity"].sum()

    print("\n" + "=" * 60)
    print("ОСНОВНЫЕ ПОКАЗАТЕЛИ")
    print("=" * 60)
    print(f"Общая выручка: {total:,.0f} тенге")
    print(f"Продано единиц товара: {total_units}")
    print(f"Количество записей: {len(df)}")
    print(f"Количество категорий: {df['category'].nunique()}")
    print(f"Средняя цена: {df['price'].mean():,.2f} тенге")
    print(f"Средняя выручка на запись: {df['revenue'].mean():,.2f} тенге")

    products = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    categories = df.groupby("category")["revenue"].sum().sort_values(ascending=False)

    print("\nВыручка по товарам:")
    print(products)
    print("\nВыручка по категориям:")
    print(categories)

    print("\nТоп-3 товара по выручке:")
    print(products.head(3))

    df["sale_date"] = pd.to_datetime(df["sale_date"])
    daily = df.groupby("sale_date")["revenue"].sum().sort_index()
    daily_units = df.groupby("sale_date")["quantity"].sum().sort_index()

    print("\nВыручка по датам:")
    print(daily)

    best_day = daily.idxmax()
    worst_day = daily.idxmin()
    print(f"\nДень с максимальной выручкой: {best_day:%Y-%m-%d} ({daily.max():,.0f} тенге)")
    print(f"День с минимальной выручкой: {worst_day:%Y-%m-%d} ({daily.min():,.0f} тенге)")

    check_quality(df)
    investigate_outlier(df)
    products, categories, daily, daily_units = build_charts(df)

    top_product = products.index[0]
    top_category = categories.index[0]
    top_category_share = categories.iloc[0] / categories.sum() * 100

    print("\n" + "=" * 60)
    print("АНАЛИТИЧЕСКИЕ ВЫВОДЫ")
    print("=" * 60)
    print(f"1. Общая выручка магазина составила {total:,.0f} тенге.")
    print(
        f"2. Наибольшую выручку приносит товар «{top_product}» "
        f"({products.iloc[0]:,.0f} тенге)."
    )
    print(
        f"3. Категория «{top_category}» обеспечивает "
        f"{top_category_share:.1f}% всей выручки."
    )
    print(
        f"4. Максимальная дневная выручка зафиксирована {best_day:%Y-%m-%d}, "
        f"минимальная — {worst_day:%Y-%m-%d}."
    )
    print(
        "5. Пропусков и полных дубликатов в данных нет, "
        "но перед анализом всегда нужно проверять качество данных."
    )
    print(
        "6. Единичный выброс (цена 15 000 000 тенге) заметно искажает среднее "
        "значение, поэтому для устойчивых выводов лучше использовать медиану."
    )


if __name__ == "__main__":
    main()
