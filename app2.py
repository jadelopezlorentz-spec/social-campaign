import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Page configuration ---
st.set_page_config(page_title="L'Oréal Infinity Lash 3D", layout="wide")

# --- Check if image files exist ---
if not os.path.exists("assets/logo.png"):
    st.error("Logo file not found in assets/")
if not os.path.exists("assets/Mascara.jpg"):
    st.error("Mascara file not found in assets/")

# --- Header ---
st.image("assets/logo.png", width=200)
st.title("💄 L'Oréal Infinity Lash 3D – Marketing Dashboard")
st.markdown("Tracking the performance of a multi-channel digital campaign – fictive data")

# --- Product image ---
st.image("assets/Mascara.jpg", width=250, caption="Infinity Lash 3D – Fictive Product")

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
