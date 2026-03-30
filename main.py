import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openpyxl
# Title
st.title("Electricity Market Dashboard")

# Upload file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Clean dataset
    df = df.iloc[3:].copy()
    df.columns = ["Date", "Hour", "Time Block", "Purchase Bid", "Sell Bid", "MCV", "Final Scheduled Volume", "MCP"]

    df = df.dropna(subset=["Date"])
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

    for col in ["Purchase Bid", "Sell Bid", "MCV", "Final Scheduled Volume", "MCP"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna()

    st.success("Data loaded successfully!")

    # Sidebar filters
    st.sidebar.header("Filters")
    selected_hour = st.sidebar.slider("Select Hour", 1, 24, (1, 24))

    filtered_df = df[(df["Hour"] >= selected_hour[0]) & (df["Hour"] <= selected_hour[1])]

    # KPI metrics
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)

    col1.metric("Avg MCP", f"{filtered_df['MCP'].mean():.2f}")
    col2.metric("Max MCP", f"{filtered_df['MCP'].max():.2f}")
    col3.metric("Min MCP", f"{filtered_df['MCP'].min():.2f}")

    # Price vs Hour
    st.subheader("MCP vs Hour")
    hourly_price = filtered_df.groupby("Hour")["MCP"].mean()

    fig1, ax1 = plt.subplots()
    hourly_price.plot(ax=ax1)
    ax1.set_xlabel("Hour")
    ax1.set_ylabel("MCP")
    st.pyplot(fig1)

    # Demand vs Supply
    st.subheader("Demand vs Supply")
    fig2, ax2 = plt.subplots()
    ax2.plot(filtered_df["Purchase Bid"].values, label="Demand")
    ax2.plot(filtered_df["Sell Bid"].values, label="Supply")
    ax2.legend()
    st.pyplot(fig2)

    # Correlation heatmap (simple)
    st.subheader("Correlation Matrix")
    corr = filtered_df[["Purchase Bid", "Sell Bid", "MCV", "MCP"]].corr()
    st.dataframe(corr)

    # Peak hour detection
    st.subheader("Peak Price Hour")
    peak_hour = hourly_price.idxmax()
    st.write(f"Highest price occurs at Hour: **{peak_hour}**")

    # Raw data
    st.subheader("Raw Data")
    st.dataframe(filtered_df)

else:
    st.info("Please upload your dataset to begin.")
