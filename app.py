import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

# page config
st.set_page_config(page_title="PhonePe Transaction Insights", layout="wide")

# title
st.title("📱 PhonePe Transaction Insights Dashboard")
st.markdown("Analysis of PhonePe transactions from 2018 to 2024")

# loading data
base_path = os.path.join(os.path.dirname(__file__), "data")

@st.cache_data
def load_agg_transaction():
    agg_trans = []
    path = os.path.join(base_path, "aggregated", "transaction", "country", "india")
    for year in os.listdir(path):
        year_path = os.path.join(path, year)
        if os.path.isdir(year_path) and year.isdigit():
            for file in os.listdir(year_path):
                if file.endswith(".json"):
                    quarter = int(file.replace(".json", ""))
                    with open(os.path.join(year_path, file)) as f:
                        data = json.load(f)
                        for item in data["data"]["transactionData"]:
                            agg_trans.append({
                                "year": int(year),
                                "quarter": quarter,
                                "transaction_type": item["name"],
                                "transaction_count": item["paymentInstruments"][0]["count"],
                                "transaction_amount": round(item["paymentInstruments"][0]["amount"] / 1e7, 2)
                            })
    return pd.DataFrame(agg_trans)

@st.cache_data
def load_map_transaction():
    map_trans = []
    path = os.path.join(base_path, "map", "transaction", "hover", "country", "india")
    for year in os.listdir(path):
        year_path = os.path.join(path, year)
        if os.path.isdir(year_path) and year.isdigit():
            for file in os.listdir(year_path):
                if file.endswith(".json"):
                    quarter = int(file.replace(".json", ""))
                    with open(os.path.join(year_path, file)) as f:
                        data = json.load(f)
                        for item in data["data"]["hoverDataList"]:
                            map_trans.append({
                                "year": int(year),
                                "quarter": quarter,
                                "state": item["name"],
                                "transaction_count": item["metric"][0]["count"],
                                "transaction_amount": round(item["metric"][0]["amount"] / 1e7, 2)
                            })
    return pd.DataFrame(map_trans)

@st.cache_data
def load_agg_user():
    agg_user = []
    path = os.path.join(base_path, "aggregated", "user", "country", "india")
    for year in os.listdir(path):
        year_path = os.path.join(path, year)
        if os.path.isdir(year_path) and year.isdigit():
            for file in os.listdir(year_path):
                if file.endswith(".json"):
                    quarter = int(file.replace(".json", ""))
                    with open(os.path.join(year_path, file)) as f:
                        data = json.load(f)
                        users = data["data"]["aggregated"]
                        agg_user.append({
                            "year": int(year),
                            "quarter": quarter,
                            "registered_users": users["registeredUsers"],
                            "app_opens": users["appOpens"]
                        })
    return pd.DataFrame(agg_user)

# load all data
df_agg_trans = load_agg_transaction()
df_map_trans = load_map_transaction()
df_agg_user = load_agg_user()

# sidebar filters
st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox("Select Year", sorted(df_agg_trans["year"].unique(), reverse=True))
selected_quarter = st.sidebar.selectbox("Select Quarter", [1, 2, 3, 4])

# filtered data
filtered_trans = df_agg_trans[(df_agg_trans["year"] == selected_year) & (df_agg_trans["quarter"] == selected_quarter)]
filtered_map = df_map_trans[(df_map_trans["year"] == selected_year) & (df_map_trans["quarter"] == selected_quarter)]

# metrics row
col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", f"{filtered_trans['transaction_count'].sum():,.0f}")
col2.metric("Total Amount (Cr)", f"₹ {filtered_trans['transaction_amount'].sum():,.2f}")
col3.metric("Registered Users", f"{df_agg_user[df_agg_user['year'] == selected_year]['registered_users'].sum():,.0f}")

st.markdown("---")

# row 1 - two charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Transaction Type by Count")
    fig1 = px.bar(filtered_trans, x="transaction_type", y="transaction_count",
                  color="transaction_type", title="Transaction Count by Type")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Transaction Type by Amount")
    fig2 = px.pie(filtered_trans, names="transaction_type", values="transaction_amount",
                  title="Transaction Amount Share by Type")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# row 2 - state wise chart
st.subheader("Top 10 States by Transaction Amount (Crores)")
top_states = filtered_map.groupby("state")["transaction_amount"].sum().sort_values(ascending=False).head(10).reset_index()
fig3 = px.bar(top_states, x="transaction_amount", y="state", orientation="h",
              color="transaction_amount", color_continuous_scale="Blues",
              title="Top 10 States by Transaction Amount")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# row 3 - yearly trend
st.subheader("Yearly Transaction Growth")
yearly = df_agg_trans.groupby("year")["transaction_count"].sum().reset_index()
fig4 = px.line(yearly, x="year", y="transaction_count", markers=True,
               title="Yearly Transaction Count Growth")
st.plotly_chart(fig4, use_container_width=True)