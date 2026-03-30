import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(layout="wide")

st.title("Advanced Electricity Market Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    # ------------------ DATA CLEANING ------------------
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    df = df.iloc[3:].copy()
    df.columns = ["Date", "Hour", "Time Block", "Purchase Bid", "Sell Bid", "MCV", "Final Scheduled Volume", "MCP"]

    df = df.dropna(subset=["Date"])
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

    for col in ["Purchase Bid", "Sell Bid", "MCV", "Final Scheduled Volume", "MCP"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna()

    # Sidebar filters
    st.sidebar.header("Filters")
    hour_range = st.sidebar.slider("Select Hour", 1, 24, (1, 24))
    df = df[(df["Hour"] >= hour_range[0]) & (df["Hour"] <= hour_range[1])]

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview",
        "Forecasting",
        "Heatmap",
        "Volatility & Strategy"
    ])

    # ------------------ TAB 1: OVERVIEW ------------------
    with tab1:

        st.subheader("Key Metrics")

        col1, col2, col3 = st.columns(3)
        col1.metric("Avg MCP", f"{df['MCP'].mean():.2f}")
        col2.metric("Max MCP", f"{df['MCP'].max():.2f}")
        col3.metric("Min MCP", f"{df['MCP'].min():.2f}")

        st.subheader("MCP vs Hour")

        hourly_price = df.groupby("Hour")["MCP"].mean()

        fig, ax = plt.subplots()
        hourly_price.plot(ax=ax)
        st.pyplot(fig)

        st.subheader("Demand vs Supply")

        fig2, ax2 = plt.subplots()
        ax2.plot(df["Purchase Bid"].values, label="Demand")
        ax2.plot(df["Sell Bid"].values, label="Supply")
        ax2.legend()
        st.pyplot(fig2)

    # ------------------ TAB 2: FORECASTING ------------------
    with tab2:

        st.subheader("MCP Prediction Model")

        df_model = df.copy()

        # Feature engineering
        df_model["Hour"] = df_model["Hour"].astype(int)

        X = df_model[["Hour", "Purchase Bid", "Sell Bid", "MCV"]]
        y = df_model["MCP"]

        model = LinearRegression()
        model.fit(X, y)

        st.write("Model trained on historical data")

        # User input
        st.subheader("Predict Next MCP")

        hour = st.slider("Hour", 1, 24, 12)
        demand = st.number_input("Expected Demand (MW)", value=10000)
        supply = st.number_input("Expected Supply (MW)", value=10000)
        mcv = st.number_input("Expected MCV", value=9000)

        pred = model.predict([[hour, demand, supply, mcv]])

        st.success(f"Predicted MCP: {pred[0]:.2f} Rs/MWh")

    # ------------------ TAB 3: HEATMAP ------------------
    with tab3:

        st.subheader("Price Heatmap (Hour vs Day)")

        df["Day"] = df["Date"].dt.day

        pivot = df.pivot_table(values="MCP", index="Hour", columns="Day")

        fig3, ax3 = plt.subplots()
        c = ax3.imshow(pivot, aspect='auto')

        plt.colorbar(c)
        ax3.set_xlabel("Day")
        ax3.set_ylabel("Hour")

        st.pyplot(fig3)

    # ------------------ TAB 4: VOLATILITY & STRATEGY ------------------
    with tab4:

        st.subheader("Volatility Tracker")

        df["Rolling Mean"] = df["MCP"].rolling(10).mean()
        df["Rolling Std"] = df["MCP"].rolling(10).std()

        df["Spike"] = df["MCP"] > (df["Rolling Mean"] + 2 * df["Rolling Std"])

        spikes = df[df["Spike"] == True]

        st.write(f"Detected {len(spikes)} price spikes")

        fig4, ax4 = plt.subplots()
        ax4.plot(df["MCP"].values, label="MCP")
        ax4.scatter(spikes.index, spikes["MCP"], label="Spikes")
        ax4.legend()

        st.pyplot(fig4)

        # Strategy Panel
        st.subheader("Trading Strategy")

        hourly_avg = df.groupby("Hour")["MCP"].mean()

        best_buy = hourly_avg.idxmin()
        best_sell = hourly_avg.idxmax()

        st.success(f"Best hour to BUY: {best_buy}")
        st.success(f"Best hour to SELL: {best_sell}")

        st.write("Strategy Insight:")
        st.write("""
        - Buy during low MCP hours
        - Sell during high MCP hours
        - Avoid high volatility spikes
        """)

else:
    st.info("Upload your dataset to start")