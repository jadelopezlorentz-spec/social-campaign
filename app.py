import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Page configuration ---
st.set_page_config(page_title="INFINITY Lash 3D", layout="wide")

# --- Custom CSS for background gradient ---
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(to right, #B9E7FD, #3C8BB4);
            color: #333;
        }
        .header-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px;
        }
        .header-container img {
            height: 50px;
        }
        .header-container h1 {
            text-align: center;
            flex-grow: 1;
            margin: 0;
            font-size: 2.5rem;
            font-weight: bold;
        }
        .content-container {
            display: flex;
            justify-content: space-between;
            padding: 20px;
        }
        .content-container .text-content {
            width: 48%;
        }
        .content-container .image-content {
            width: 48%;
        }
        .content-container img {
            width: 100%;
            border-radius: 10px;
        }
        .section-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .section-text {
            font-size: 1rem;
            line-height: 1.6;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
    <div class="header-container">
        <img src="assets/logo.png" alt="Logo L'Oréal">
        <h1>INFINITY Lash 3D</h1>
        <img src="assets/Mascara.png" alt="Mascara Image">
    </div>
""", unsafe_allow_html=True)

# --- Main content ---
st.markdown("""
    <div class="content-container">
        <div class="text-content">
            <p class="section-title">Project Overview</p>
            <p class="section-text">
                This project simulates the digital marketing performance of a fictitious L'Oréal product, Infinity Lash 3D, a next-generation mascara offering maximum 3D volume and definition.
                The objective of this dashboard is to track multi-channel campaign performance across Instagram, TikTok, and YouTube, for Paris, London, and New York, and visualize key KPIs including Impressions, Clicks, CTR, CPC, and Engagement.
                This project showcases my skills in digital marketing, data analytics, and interactive visualization using Python, Streamlit, Plotly, and for the visual Adobe Firefly.
            </p>
        </div>
        <div class="image-content">
            <p class="section-title">Campaign Concept</p>
            <p class="section-text">
                Product: Infinity Lash 3D<br>
                Promotional Message: “Maximize your lashes in 3D – bold, defined, unstoppable.”<br>
                Target Audience: 18-35 years old, beauty enthusiasts, social media active<br>
                Channels: Instagram, TikTok, YouTube<br>
                Markets: New York, Paris, London<br>
                Campaign Type: Sponsored posts, short video tutorials, influencer partnerships
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Load data ---
df = pd.read_csv("data/loreal_infinitylash.csv", parse_dates=["Date"])

# --- KPI cards ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Impressions", f"{df['Impressions'].sum():,}")
col2.metric("Total Clicks", f"{df['Clicks'].sum():,}")
col3.metric("Total Spend (€)", f"{df['Spend (€)'].sum():,}")
col4.metric("Avg CTR (%)", f"{df['CTR (%)'].mean():.2f}")

# --- Line charts ---
st.subheader("📈 KPIs Over Time")
fig_line = px.line(df, x="Date", y=["Impressions","Clicks"], color="Channel",
                   title="Impressions & Clicks Over Time by Channel", markers=True, template="plotly_dark")
st.plotly_chart(fig_line, use_container_width=True)

fig_ctr = px.line(df, x="Date", y="CTR (%)", color="Channel",
                  title="CTR (%) Over Time by Channel", markers=True, template="plotly_white")
st.plotly_chart(fig_ctr, use_container_width=True)

fig_cpc = px.bar(df, x="Date", y="CPC (€)", color="Channel",
                 title="CPC per Day and Channel", template="ggplot2")
st.plotly_chart(fig_cpc, use_container_width=True)

# --- Interactive Map ---
st.subheader("🌍 Geographical Distribution of Clicks")
coords = {
    "New York": (40.7128, -74.0060),
    "Paris": (48.8566, 2.3522),
    "London": (51.5074, -0.1278),
    "Tokyo": (35.6895, 139.6917),
    "Sydney": (-33.8688, 151.2093)
}
df["lat"] = df["City"].apply(lambda x: coords[x][0])
df["lon"] = df["City"].apply(lambda x: coords[x][1])

fig_map = px.scatter_mapbox(df, lat="lat", lon="lon", size="Clicks",
                            color="Channel", hover_name="City",
                            zoom=1.5, mapbox_style="carto-positron",
                            title="Clicks per City and Channel")
st.plotly_chart(fig_map, use_container_width=True)

# --- Insights / Conclusion ---
st.subheader("🔎 Insights & Conclusion")
st.write("""
- TikTok shows the highest CTR (3.0-3.1%) and relatively lower CPC → prioritize this channel.
- New York is the top-performing city in terms of impressions and clicks.
- This dashboard demonstrates my ability to analyze and visualize KPIs from an international digital campaign.
""")

st.markdown("💡 [My LinkedIn](https://www.linkedin.com/in/yourprofile)")
