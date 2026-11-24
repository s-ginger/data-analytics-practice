import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "shop.db"

st.set_page_config(
    page_title="Аналитика магазина",
    layout="wide",
)


@st.cache_data(ttl=10)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    if df.empty:
        return df
    df["revenue"] = df["price"] * df["quantity"]
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    return df


st.title("Аналитика интернет-магазина")
st.caption(
    "Интерактивная панель по данным таблицы sales из базы shop.db. "
    "Фильтры пересчитывают показатели и графики."
)

if not DB_PATH.exists():
    st.error("База данных shop.db не найдена. Сначала запустите: python setup_db.py")
    st.stop()

df = load_data()

if df.empty:
    st.warning("В базе данных нет записей. Запустите: python setup_db.py")
    st.stop()

st.sidebar.header("Фильтры")

if st.sidebar.button("Обновить данные", width="stretch"):
    st.cache_data.clear()
    st.rerun()

categories = sorted(df["category"].unique())
selected_categories = st.sidebar.multiselect(
    "Категории товаров",
    categories,
    default=categories,
)

if selected_categories:
    available_products = sorted(
        df[df["category"].isin(selected_categories)]["product"].unique()
    )
else:
    available_products = []

selected_products = st.sidebar.multiselect(
    "Товары",
    available_products,
    default=available_products,
)

st.sidebar.divider()
st.sidebar.metric("Записей в базе", len(df))
st.sidebar.metric("Категорий в базе", df["category"].nunique())
st.sidebar.metric("Товаров в базе", df["product"].nunique())

filtered = df[
    df["category"].isin(selected_categories) & df["product"].isin(selected_products)
]

if filtered.empty:
    st.warning(
        "Нет данных для выбранных категорий и товаров. "
        "Измените фильтры в левой панели."
    )
    st.stop()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Общая выручка", f'{filtered["revenue"].sum():,.0f} ₸')
col2.metric("Продано товаров", f'{int(filtered["quantity"].sum()):,}'.replace(",", " "))
col3.metric("Количество продаж", len(filtered))
col4.metric("Средняя цена", f'{filtered["price"].mean():,.0f} ₸')

st.divider()

revenue_by_product = (
    filtered.groupby("product", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
)
revenue_by_category = filtered.groupby("category", as_index=False)["revenue"].sum()
units_by_product = (
    filtered.groupby("product", as_index=False)["quantity"]
    .sum()
    .sort_values("quantity", ascending=False)
)
daily_revenue = filtered.groupby("sale_date", as_index=False)["revenue"].sum()

left, right = st.columns(2)

with left:
    fig = px.bar(
        revenue_by_product,
        x="product",
        y="revenue",
        title="Выручка по товарам",
        labels={"product": "Товар", "revenue": "Выручка, тенге"},
        color="revenue",
        color_continuous_scale="Blues",
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
    st.plotly_chart(fig, width="stretch")

with right:
    fig = px.pie(
        revenue_by_category,
        names="category",
        values="revenue",
        title="Доля категорий в выручке",
        hole=0.35,
    )
    st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)

with left:
    fig = px.line(
        daily_revenue,
        x="sale_date",
        y="revenue",
        markers=True,
        title="Динамика выручки по датам",
        labels={"sale_date": "Дата", "revenue": "Выручка, тенге"},
    )
    st.plotly_chart(fig, width="stretch")

with right:
    fig = px.bar(
        units_by_product,
        x="product",
        y="quantity",
        title="Количество проданных единиц",
        labels={"product": "Товар", "quantity": "Количество, шт."},
        color="quantity",
        color_continuous_scale="Greens",
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
    st.plotly_chart(fig, width="stretch")

st.divider()
st.subheader("Таблица продаж")

table = filtered.copy()
table["sale_date"] = table["sale_date"].dt.strftime("%Y-%m-%d")
table = table.rename(
    columns={
        "id": "ID",
        "product": "Товар",
        "category": "Категория",
        "price": "Цена, ₸",
        "quantity": "Количество",
        "sale_date": "Дата продажи",
        "revenue": "Выручка, ₸",
    }
)

st.dataframe(
    table[["ID", "Товар", "Категория", "Цена, ₸", "Количество", "Дата продажи", "Выручка, ₸"]],
    width="stretch",
    hide_index=True,
)

csv = table.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Скачать CSV",
    csv,
    file_name="sales_report.csv",
    mime="text/csv",
)

with st.expander("О приложении"):
    st.write(
        "Данные загружаются напрямую из SQLite (shop.db). "
        "Выручка рассчитывается как цена × количество. "
        "Все показатели и диаграммы пересчитываются при изменении фильтров. "
        "Кнопка «Обновить данные» сбрасывает кэш, если база была изменена."
    )
