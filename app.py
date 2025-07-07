# ---Import Libraries---
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Dashboard Analisis Penjualan Adidas",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/Adidas_Salesdata.csv")
    df['Invoice Date'] = pd.to_datetime(df['Invoice Date'])
    return df

df_sales = load_data()


# --- Sidebar Filter ---
st.sidebar.header("🔍 Filter Data")

states = df_sales["State"].unique().tolist()
selected_states = st.sidebar.multiselect(
    "Pilih State:",
    options=states,
    default=states
)

categories = df_sales["Product Category"].unique().tolist()
selected_categories = st.sidebar.multiselect(
    "Pilih Product Category:",
    options=categories,
    default=categories
)

min_date = df_sales["Invoice Date"].min()
max_date = df_sales["Invoice Date"].max()

start_date, end_date = st.sidebar.date_input(
    "Pilih Rentang Tanggal:",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# --- Apply Filter ---
df_filtered = df_sales[
    (df_sales["State"].isin(selected_states)) &
    (df_sales["Product Category"].isin(selected_categories)) &
    (df_sales["Invoice Date"] >= pd.to_datetime(start_date)) &
    (df_sales["Invoice Date"] <= pd.to_datetime(end_date))
]

# --- Debug Info ---
st.sidebar.write("Data rows:", df_filtered.shape[0])


# --- Judul Dashboard ---
st.title("📈 Dashboard Analisis Penjualan Adidas 🛍️")
st.markdown("Dashboard interaktif ini memuat filter dinamis berdasarkan State, Product Category, dan Tanggal.")
st.markdown("---")
 

# --- HITUNG KPI ---
total_sales = df_sales['Total Sales'].sum()
total_profit = df_sales['Operating Profit'].sum()
total_orders = df_sales['Invoice Date'].nunique()  

# --- TAMPILKAN KPI DALAM KOL 1 BARIS ---

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Total Sales", f"${total_sales:,.2f}")

with col2:
    st.metric("📈 Operating Profit", f"${total_profit:,.2f}")

with col3:
    st.metric("📊 Total Orders", total_orders)

st.divider()

# --- PROFIT BY STATE (TOP 10) ---
profit_state = (
    df_sales.groupby("State")["Operating Profit"]
    .sum()
    .reset_index()
    .nlargest(10, 'Operating Profit')
    .sort_values(by="Operating Profit", ascending=True)
)

# --- SALES IN NEW YORK BY CATEGORY ---
ca_category = (
    df_sales[df_sales["State"] == "New York"]
    .groupby("Product Category")["Total Sales"]
    .sum()
    .reset_index()
)

# --- melihat top operating profit by stage ---
st.header("📈 Profit & Sales Breakdown")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 10 Operating Profit by State")
    st.markdown("Menampilkan negara bagian dengan profit operasional tertinggi.")
    
    fig_profit_state = px.bar(
        profit_state,
        x="Operating Profit",
        y="State",
        orientation="h",
        template="plotly_white",
        color_discrete_sequence=["#2E86C1"]
    )
    fig_profit_state.update_layout(
        font=dict(family="Arial", size=12),
        xaxis_title="Operating Profit",
        yaxis_title="State",
    )
    st.plotly_chart(fig_profit_state, use_container_width=True)

with col2:
    st.subheader("🗂️ Total Sales in New York by Product Category") # Mengapa New York ? karena New York merupakan wilayah dengan operating profit paling tinggi
    st.markdown("Distribusi penjualan di New York berdasarkan kategori produk.")
    
    fig_ca_category = px.pie(
        ca_category,
        names="Product Category",
        values="Total Sales",
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_ca_category.update_traces(textinfo='percent+label')
    fig_ca_category.update_layout(
        font=dict(family="Arial", size=12),
    )
    st.plotly_chart(fig_ca_category, use_container_width=True)

st.divider()


# --- TOTAL SALES APPAREL IN New York ---
# Mengapa Apparel di New York? Karena Apparel merupakan kategori produk dengan total sales paling tinggi
st.header("🧥 Apparel Sales in New York")

# --- Filter Data ---
df_ca_apparel = df_sales[
    (df_sales["State"] == "New York") & (df_sales["Product Category"] == "Apparel")
]

# --- Sales by Sales Method ---
ca_apparel_sales = (
    df_ca_apparel.groupby("Sales Method")["Total Sales"]
    .sum().reset_index()
)

# --- Sales by Retailer ---
ca_apparel_retailer = (
    df_ca_apparel.groupby("Retailer")["Total Sales"]
    .sum().reset_index()
    .sort_values(by="Total Sales", ascending=False)
)

# ============================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("🛒 Apparel Sales in New York by Sales Method")
    st.markdown("Menampilkan total penjualan produk Apparel di New York berdasarkan metode penjualan.")
    fig_ca_apparel_method = px.bar(
        ca_apparel_sales,
        x="Sales Method",
        y="Total Sales",
        template="plotly_white",
        color_discrete_sequence=["#28B463"],
    )
    fig_ca_apparel_method.update_layout(
        font=dict(family="Arial", size=12),
        xaxis_title="Sales Method",
        yaxis_title="Total Sales",
    )
    st.plotly_chart(fig_ca_apparel_method, use_container_width=True)

with col2:
    st.subheader("🏪 Apparel Sales in New York by Retailer")
    st.markdown("Menampilkan total penjualan produk Apparel di New York berdasarkan Retailer.")
    fig_ca_apparel_retailer = px.bar(
        ca_apparel_retailer,
        x="Retailer",
        y="Total Sales",
        template="plotly_white",
        color_discrete_sequence=["#F39C12"],
    )
    fig_ca_apparel_retailer.update_layout(
        font=dict(family="Arial", size=12),
        xaxis_title="Retailer",
        yaxis_title="Total Sales",
    )
    st.plotly_chart(fig_ca_apparel_retailer, use_container_width=True)


# ============================================
# --- Monthly Total Sales + Heatmap ---
st.header("📅 Monthly Sales Trend & Product Pattern")

df_sales['Month_Period'] = df_sales['Invoice Date'].dt.to_period('M').astype(str)
df_sales['Month_Name'] = df_sales['Invoice Date'].dt.month_name()

# ---  Monthly Total Sales ---
monthly_sales = df_sales.groupby("Month_Period")["Total Sales"].sum().reset_index()

fig_monthly_sales = px.line(
    monthly_sales,
    x="Month_Period",
    y="Total Sales",
    title="📈 Monthly Total Sales",
    markers=True,
    template="plotly_white",
    color_discrete_sequence=["#2980B9"]
)

fig_monthly_sales.update_layout(
    xaxis_title="Month",
    yaxis_title="Total Sales",
    font=dict(family="Arial", size=12)
)

# --- Monthly Sales by Product Category ---
heatmap = (
    df_sales.groupby(["Month_Name", "Product Category"])["Total Sales"]
    .sum().reset_index()
)

# Biar urut, atur kategori nama bulan (Jan ➜ Dec)
from pandas.api.types import CategoricalDtype
month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
heatmap["Month_Name"] = heatmap["Month_Name"].astype(
    CategoricalDtype(categories=month_order, ordered=True)
)

fig_heatmap = px.density_heatmap(
    heatmap,
    x="Month_Name",
    y="Product Category",
    z="Total Sales",
    title="🔥 Monthly Sales Heatmap by Product Category",
    color_continuous_scale="Viridis",
    template="plotly_white"
)

fig_heatmap.update_layout(
    font=dict(family="Arial", size=12),
    xaxis_title="Month",
    yaxis_title="Product Category"
)

# ---  Mengatur layout ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Monthly Total Sales")
    st.plotly_chart(fig_monthly_sales, use_container_width=True)

with col2:
    st.subheader("🔥 Sales Heatmap by Product Category")
    st.plotly_chart(fig_heatmap, use_container_width=True)