import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

st.set_page_config(layout="wide")

st.title("Electricity Market Intelligence Dashboard")

file = st.file_uploader("Upload dataset", type=["xlsx"])

if file:

    df = pd.read_excel(file, engine="openpyxl")
    df = df.iloc[3:].copy()

    df.columns = ["Date", "Hour", "Time Block", "Purchase Bid", "Sell Bid", "MCV", "Final Scheduled Volume", "MCP"]

    df = df.dropna(subset=["Date"])
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    for col in ["Purchase Bid", "Sell Bid", "MCV", "Final Scheduled Volume", "MCP"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()
    df["Hour"] = df["Hour"].astype(int)

    df["Gap"] = df["Purchase Bid"] - df["Sell Bid"]
    df["Scarcity"] = df["Purchase Bid"] / df["Sell Bid"]
    df["Volatility"] = df["MCP"].rolling(24).std()
    df["Ramp"] = df["MCV"].diff()
    df["Efficiency"] = df["MCV"] / df["Purchase Bid"]
    df["Day"] = df["Date"].dt.day
    df["DayOfWeek"] = df["Date"].dt.day_name()

    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview",
        "Forecasting",
        "Heatmap",
        "Market Intelligence"
    ])

    with tab1:

        col1, col2, col3 = st.columns(3)
        col1.metric("Average MCP", f"{df['MCP'].mean():.2f}")
        col2.metric("Maximum MCP", f"{df['MCP'].max():.2f}")
        col3.metric("Minimum MCP", f"{df['MCP'].min():.2f}")

        hourly = df.groupby("Hour")["MCP"].mean()

        fig1, ax1 = plt.subplots()
        hourly.plot(ax=ax1)
        ax1.set_title("Average MCP by Hour")
        ax1.set_xlabel("Hour")
        ax1.set_ylabel("Market Clearing Price")
        ax1.legend(["MCP"])
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots()
        ax2.plot(df["Purchase Bid"].values, label="Purchase Bid")
        ax2.plot(df["Sell Bid"].values, label="Sell Bid")
        ax2.set_title("Demand and Supply")
        ax2.set_xlabel("Time Index")
        ax2.set_ylabel("Megawatt")
        ax2.legend()
        st.pyplot(fig2)

    with tab2:

        X = df[["Hour", "Purchase Bid", "Sell Bid", "MCV"]]
        y = df["MCP"]

        model = LinearRegression()
        model.fit(X, y)

        hour = st.slider("Hour", 1, 24, 12)
        demand = st.number_input("Purchase Bid", value=10000)
        supply = st.number_input("Sell Bid", value=10000)
        mcv = st.number_input("MCV", value=9000)

        pred = model.predict([[hour, demand, supply, mcv]])
        st.write(f"Predicted MCP: {pred[0]:.2f}")

    with tab3:

        pivot = df.pivot_table(values="MCP", index="Hour", columns="Day")

        fig3, ax3 = plt.subplots()
        c = ax3.imshow(pivot, aspect="auto")
        fig3.colorbar(c)
        ax3.set_title("Hour vs Day MCP Heatmap")
        ax3.set_xlabel("Day of Month")
        ax3.set_ylabel("Hour of Day")
        st.pyplot(fig3)

    with tab4:

        fig4, ax4 = plt.subplots()
        ax4.plot(df["Gap"].values, label="Demand Supply Gap")
        ax4.set_title("Demand Supply Gap")
        ax4.set_xlabel("Time Index")
        ax4.set_ylabel("Megawatt")
        ax4.legend()
        st.pyplot(fig4)

        fig5, ax5 = plt.subplots()
        ax5.plot(df["Scarcity"].values, label="Scarcity Index")
        ax5.set_title("Scarcity Index")
        ax5.set_xlabel("Time Index")
        ax5.set_ylabel("Ratio")
        ax5.legend()
        st.pyplot(fig5)

        fig6, ax6 = plt.subplots()
        ax6.plot(df["Volatility"].values, label="Volatility")
        ax6.set_title("Price Volatility")
        ax6.set_xlabel("Time Index")
        ax6.set_ylabel("Price Variation")
        ax6.legend()
        st.pyplot(fig6)

        fig7, ax7 = plt.subplots()
        ax7.plot(df["Ramp"].values, label="Ramp")
        ax7.set_title("Ramp Changes")
        ax7.set_xlabel("Time Index")
        ax7.set_ylabel("Megawatt Change")
        ax7.legend()
        st.pyplot(fig7)

        fig8, ax8 = plt.subplots()
        ax8.plot(df["Efficiency"].values, label="Market Efficiency")
        ax8.set_title("Market Efficiency")
        ax8.set_xlabel("Time Index")
        ax8.set_ylabel("Ratio")
        ax8.legend()
        st.pyplot(fig8)

        duration = df["MCP"].sort_values(ascending=False).reset_index(drop=True)

        fig9, ax9 = plt.subplots()
        ax9.plot(duration.values, label="Price Duration Curve")
        ax9.set_title("Price Duration Curve")
        ax9.set_xlabel("Sorted Time Index")
        ax9.set_ylabel("Market Clearing Price")
        ax9.legend()
        st.pyplot(fig9)

        hourly_avg = df.groupby("Hour")["MCP"].mean()
        buy_hour = hourly_avg.idxmin()
        sell_hour = hourly_avg.idxmax()

        st.write(f"Best hour to buy: {buy_hour}")
        st.write(f"Best hour to sell: {sell_hour}")

        profit = hourly_avg.max() - hourly_avg.min()
        st.write(f"Expected spread: {profit:.2f}")

        cluster_data = df[["Purchase Bid", "Sell Bid", "MCP"]]

        kmeans = KMeans(n_clusters=3, n_init=10)
        df["Cluster"] = kmeans.fit_predict(cluster_data)

        fig10, ax10 = plt.subplots()
        ax10.scatter(df["Purchase Bid"], df["MCP"], c=df["Cluster"])
        ax10.set_title("Market State Clustering")
        ax10.set_xlabel("Purchase Bid")
        ax10.set_ylabel("Market Clearing Price")
        st.pyplot(fig10)

else:
    st.write("Upload dataset to begin")