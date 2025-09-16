# app.py — no-scroll gallery, centered filters, best hour by city, English narrative
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import base64
from pathlib import Path

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="INFINITY Lash 3D – Marketing Dashboard", layout="wide", page_icon="👁️")

# ---- paths
LOGO_PATH = Path("assets/logo.png")
PRODUCT_IMAGE_PATH = Path("assets/Mascara.png")
CSV_CLEAN = Path("data/loreal_infinitylash_clean.csv")
CSV_FALLBACK = Path("data/loreal_infinitylash.csv")

# =========================
# UTILS
# =========================
def img_to_b64(path: Path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

def ensure_metrics(df_: pd.DataFrame) -> pd.DataFrame:
    req = {"Date","City","Channel","Impressions","Clicks","Spend (€)"}
    miss = req - set(df_.columns)
    if miss:
        st.error(f"Missing required columns: {miss}")
        st.stop()
    if not pd.api.types.is_datetime64_any_dtype(df_["Date"]):
        df_["Date"] = pd.to_datetime(df_["Date"], errors="coerce")

    # Derived metrics
    df_["CTR (%)"] = np.where(df_["Impressions"]>0, df_["Clicks"]/df_["Impressions"]*100, np.nan)
    df_["CPC (€)"] = np.where(df_["Clicks"]>0, df_["Spend (€)"]/df_["Clicks"], np.nan)
    df_["CPM (€)"] = np.where(df_["Impressions"]>0, df_["Spend (€)"]/df_["Impressions"]*1000, np.nan)

    # Drop legacy/unused cols if present
    DROP_COLS = ["Creative","Influencer","Likes","Shares","Saves","Comments"]
    df_ = df_.drop(columns=[c for c in DROP_COLS if c in df_.columns], errors="ignore")

    # Optional hour
    if "Hour" in df_.columns:
        df_["Hour"] = pd.to_numeric(df_["Hour"], errors="coerce").clip(0, 23).astype("Int64")

    return df_

def weighted_ctr(d: pd.DataFrame) -> float:
    imps, clicks = d["Impressions"].sum(), d["Clicks"].sum()
    return float(clicks / imps * 100) if imps > 0 else np.nan

def fmt_int(x): 
    try: return f"{int(x):,}"
    except: return "0"

def fmt_float(x, nd=2):
    try: return f"{float(x):.{nd}f}"
    except: return f"{0:.{nd}f}"

# =========================
# CSS
# =========================
st.markdown("""
<style>
.stApp { background:#ffffff; color:#0d1b2a; }
/* HERO */
.hero {
  background: linear-gradient(180deg, #b9e7fd 0%, #3c8bb4 100%);
  color:#0a2b3a; padding:24px 28px 18px 28px;
  border-radius:0 0 20px 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}
.hero .header { display:grid; grid-template-columns:140px 1fr 140px; align-items:center; gap:16px; }
.hero h1 { margin:0; text-align:center; font-size:2.2rem; font-weight:900; letter-spacing:.2px; }
.hero .logo { width:100%; max-height:80px; object-fit:contain; }
.pills { display:flex; gap:10px; flex-direction:column; align-items:center; margin-top:8px; }
.pill { background: rgba(255,255,255,0.65); backdrop-filter: blur(6px);
  border:1px solid rgba(0,0,0,.06); border-radius:14px; padding:8px 12px; max-width:1100px;
  font-size:1.0rem; line-height:1.5; text-align:center; }
.twocols { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:14px; }
.block { background: rgba(255,255,255,0.9); border:1px solid rgba(0,0,0,.06);
  border-radius:14px; padding:14px 16px; }
.block h3 { margin:0 0 8px 0; font-size:1.05rem; font-weight:800; }
.image-block { display:flex; align-items:center; justify-content:center; min-height:240px; }
.image-block img { width:100%; max-width:480px; height:auto; border-radius:12px;
  box-shadow: 0 8px 20px rgba(0,0,0,.15); border:1px solid rgba(0,0,0,.06); object-fit:cover; }

/* Filters (centered, single row) */
.filters-row {
  display:flex; justify-content:center; align-items:center; gap:14px;
  background:#f7fbff; border:1px solid rgba(0,0,0,.06); border-radius:12px;
  padding:8px 12px; margin-top:12px;
}
.filters-row > div { min-width:260px; }

/* KPIs */
.kpis-center {
  display:flex; align-items:center; justify-content:center; gap:28px;
  margin: 16px auto 6px auto; flex-wrap:wrap;
}
.kpi-card { text-align:center; min-width:180px; }
.kpi-value { font-size:2.0rem; font-weight:900; line-height:1.0; }
.kpi-label { font-size:0.95rem; opacity:0.8; margin-top:4px; }

/* Charts container */
.section-title { font-size:1.25rem; font-weight:900; margin:18px 0 6px 0; }
.block-chart { background:#fff; border:1px solid rgba(0,0,0,.06); border-radius:12px; padding:8px 10px; }

/* Gallery header */
.gallery-head { display:flex; align-items:center; justify-content:center; gap:10px; margin-top:6px; }
.gallery-title { text-align:center; font-weight:800; font-size:1.05rem; }
.gallery-dots { text-align:center; letter-spacing:2px; opacity:.7; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

# =========================
# HERO
# =========================
def render_hero():
    logo_b64 = img_to_b64(LOGO_PATH)
    product_b64 = img_to_b64(PRODUCT_IMAGE_PATH)
    logo_html = f'<img class="logo" src="data:image/png;base64,{logo_b64}"/>' if logo_b64 else "<div></div>"
    product_html = (
        f'<img src="data:image/png;base64,{product_b64}" alt="Infinity Lash 3D"/>'
        if product_b64 else '<div style="opacity:.75;text-align:center;">Place product image at <code>assets/Mascara.png</code></div>'
    )
    st.markdown(f"""
    <div class="hero">
      <div class="header">
        {logo_html}
        <h1>INFINITY Lash 3D – Marketing Dashboard</h1>
        <div></div>
      </div>

      <div class="pills">
        <div class="pill">
          This project simulates the digital marketing performance of a fictitious L'Oréal product, <b>Infinity Lash 3D</b>, a next-gen mascara offering maximum 3D volume and definition.
        </div>
        <div class="pill">
          The objective is to track multi-channel campaign performance across Instagram, TikTok, and YouTube for Paris, London, and New York, and visualize key KPIs: Impressions, Clicks, CTR, CPC, and Engagement.
        </div>
      </div>

      <div class="twocols">
        <div class="block">
          <h3>Campaign Concept</h3>
          <div>
            <b>Product:</b> Infinity Lash 3D<br/>
            <b>Promotional Message:</b> “Maximize your lashes in 3D – bold, defined, unstoppable.”<br/>
            <b>Target Audience:</b> 18–35, beauty enthusiasts, social-media active<br/>
            <b>Channels:</b> Instagram, TikTok, YouTube<br/>
            <b>Markets:</b> New York, Paris, London<br/>
            <b>Campaign Type:</b> Sponsored posts, short video tutorials, influencer partnerships
          </div>
        </div>
        <div class="block image-block">
          {product_html}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

render_hero()

# =========================
# DATA
# =========================
if CSV_CLEAN.exists():
    df = pd.read_csv(CSV_CLEAN, parse_dates=["Date"])
elif CSV_FALLBACK.exists():
    df = pd.read_csv(CSV_FALLBACK, parse_dates=["Date"])
else:
    st.error("❗ CSV not found. Put your file at `data/loreal_infinitylash_clean.csv` or `data/loreal_infinitylash.csv`.")
    st.stop()

df = ensure_metrics(df)

# =========================
# FILTERS — centered, single row (Channels & Cities only)
# =========================
channels = sorted(df["Channel"].dropna().unique())
cities = sorted(df["City"].dropna().unique())

st.markdown('<div class="filters-row">', unsafe_allow_html=True)
fcol1, fcol2 = st.columns(2)
with fcol1:
    sel_channels = st.multiselect("Channels", channels, default=channels)
with fcol2:
    sel_cities = st.multiselect("Cities", cities, default=cities)
st.markdown('</div>', unsafe_allow_html=True)

# Fixed aggregation for readability
granularity = "Daily"   # day-level
smooth = True           # rolling smoothing
window = 7              # 7-day rolling

# Apply filters
mask = (df["Channel"].isin(sel_channels) & df["City"].isin(sel_cities))
fdf = df.loc[mask].copy()

# =========================
# KPIs (centered)
# =========================
k_impr  = fmt_int(fdf["Impressions"].sum())
k_clicks= fmt_int(fdf["Clicks"].sum())
k_spend = fmt_int(fdf["Spend (€)"].sum())
k_ctr   = fmt_float(fdf["CTR (%)"].mean(), 2)

st.markdown(f"""
<div class="kpis-center">
  <div class="kpi-card"><div class="kpi-value">{k_impr}</div><div class="kpi-label">Total Impressions (filtered)</div></div>
  <div class="kpi-card"><div class="kpi-value">{k_clicks}</div><div class="kpi-label">Total Clicks (filtered)</div></div>
  <div class="kpi-card"><div class="kpi-value">{k_spend}</div><div class="kpi-label">Total Spend (€) (filtered)</div></div>
  <div class="kpi-card"><div class="kpi-value">{k_ctr}</div><div class="kpi-label">Avg CTR (%) (filtered)</div></div>
</div>
""", unsafe_allow_html=True)

# =========================
# HELPERS (aggregation & axes)
# =========================
def aggregate(df_in: pd.DataFrame, how: str) -> pd.DataFrame:
    """Aggregate per Channel × Date and resample to a continuous timeline. Rolling smoothing optional."""
    if df_in.empty: return df_in
    out = []
    freq = {"Daily": "D", "Weekly": "W-MON", "Monthly": "MS"}[how]
    for ch, g in df_in.groupby("Channel", dropna=True):
        daily = (g.groupby(pd.to_datetime(g["Date"]).dt.normalize(), as_index=True)
                   .agg({"Impressions":"sum","Clicks":"sum","Spend (€)":"sum"})
                   .rename_axis("Date").sort_index())
        rs = daily.resample(freq).sum().fillna(0)
        rs["Channel"] = ch
        rs["CTR (%)"] = np.where(rs["Impressions"]>0, rs["Clicks"]/rs["Impressions"]*100, np.nan)
        rs["CPC (€)"] = np.where(rs["Clicks"]>0, rs["Spend (€)"]/rs["Clicks"], np.nan)
        out.append(rs.reset_index())
    agg_ = pd.concat(out, ignore_index=True).sort_values(["Channel","Date"])
    if smooth and not agg_.empty:
        for col in ["Impressions","Clicks","CTR (%)","CPC (€)"]:
            agg_[col] = agg_.groupby("Channel", group_keys=False)[col].apply(lambda s: s.rolling(window, min_periods=1).mean())
    return agg_

def tune_time_axes(fig, yfmt=",.0f", height=440, ytitle="", y0=True, y_max=None, x_dtick="M1", x_fmt="%b %Y"):
    fig.update_traces(mode="lines", line=dict(width=3))
    fig.update_layout(template="plotly_white", height=height,
                      margin=dict(l=12, r=12, t=56, b=8),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                      hovermode=False, yaxis_title=ytitle)
    fig.update_yaxes(tickformat=yfmt, showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.10)",
                     zeroline=False, ticks="outside", ticklen=6,
                     rangemode="tozero" if y0 else None,
                     range=[0, y_max] if y_max is not None else None)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.08)",
                     ticks="outside", ticklen=6, tickangle=0,
                     dtick=x_dtick, tickformat=x_fmt)
    return fig

def choose_dtick_and_fmt(d1, d2, gran):
    days = (pd.to_datetime(d2) - pd.to_datetime(d1)).days + 1
    if gran == "Daily":
        if days <= 31:  return "D1", "%d %b"
        if days <= 120: return "M1", "%b %Y"
        return "M2", "%b %Y"
    if gran == "Weekly":
        if days <= 90:  return "W1", "%d %b"
        return "M1", "%b %Y"
    return "M1", "%b %Y"

# =========================
# GRAPH GALLERY — no-scroll (arrow navigation)
# =========================
st.markdown('<div class="section-title">📈 Key Charts</div>', unsafe_allow_html=True)

# 1) Aggregate & ticks
agg = aggregate(fdf, "Daily")
x_dtick, x_fmt = choose_dtick_and_fmt(fdf["Date"].min(), fdf["Date"].max(), "Daily")

# 2) Build figures (same height)
GALLERY_HEIGHT = 420

def make_time_fig(y, yfmt, ytitle):
    fig = px.line(agg, x="Date", y=y, color="Channel", title=None)
    fig.update_layout(title=dict(text=ytitle, x=0.01, y=0.98, xanchor="left", font=dict(size=16)))
    return tune_time_axes(fig, yfmt=yfmt, height=GALLERY_HEIGHT, ytitle=ytitle,
                          y0=True,
                          y_max=float(agg[y].max()*1.12) if not agg.empty else None,
                          x_dtick=x_dtick, x_fmt=x_fmt)

def make_city_ctr_fig():
    city_ctr = (fdf.groupby("City").apply(weighted_ctr)
                .reset_index(name="CTR (%)").sort_values("CTR (%)", ascending=False))
    fig = px.bar(city_ctr, x="City", y="CTR (%)",
                 text=city_ctr["CTR (%)"].map(lambda v: f"{v:.2f}%"), title=None)
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(template="plotly_white", height=GALLERY_HEIGHT,
                      margin=dict(l=12, r=12, t=56, b=8),
                      title=dict(text="CTR (%) by City (weighted)", x=0.01, y=0.98, xanchor="left", font=dict(size=16)),
                      hovermode=False, yaxis_title="CTR (%)")
    fig.update_yaxes(tickformat=".2f",
                     range=[0, float(city_ctr["CTR (%)"].max()*1.2) if not city_ctr.empty else None],
                     showgrid=True, gridcolor="rgba(0,0,0,0.10)")
    return fig

def make_city_clicks_fig():
    city_channel = fdf.groupby(["City", "Channel"], as_index=False)[["Clicks"]].sum()
    fig = px.bar(city_channel, x="City", y="Clicks", color="Channel", barmode="stack", title=None)
    fig.update_layout(template="plotly_white", height=GALLERY_HEIGHT,
                      margin=dict(l=12, r=12, t=56, b=8),
                      title=dict(text="Clicks by City & Channel", x=0.01, y=0.98, xanchor="left", font=dict(size=16)),
                      hovermode=False, yaxis_title="Clicks")
    fig.update_yaxes(tickformat=",.0f",
                     range=[0, float(city_channel["Clicks"].max()*1.15) if not city_channel.empty else None],
                     showgrid=True, gridcolor="rgba(0,0,0,0.10)")
    return fig

def make_best_hour_by_city_fig():
    if "Hour" not in fdf.columns or fdf.dropna(subset=["Hour"]).empty:
        return None
    fdf_h = fdf.dropna(subset=["Hour"]).copy()
    fdf_h["Hour"] = fdf_h["Hour"].astype(int)

    def w_ctr(df_):
        imps, clk = df_["Impressions"].sum(), df_["Clicks"].sum()
        return float(clk/imps*100) if imps>0 else np.nan

    city_hour_ctr = fdf_h.groupby(["City","Hour"]).apply(w_ctr).reset_index(name="CTR (%)")
    best_hour = (city_hour_ctr.sort_values(["City","CTR (%)"], ascending=[True,False])
                 .groupby("City").head(1).sort_values("CTR (%)", ascending=False))

    fig = px.bar(
        best_hour, x="City", y="CTR (%)",
        text=best_hour.apply(lambda r: f"{int(r['Hour']):02d}:00", axis=1),
        title=None
    )
    fig.update_traces(textposition="outside", showlegend=False, cliponaxis=False)
    fig.update_layout(template="plotly_white", height=GALLERY_HEIGHT,
                      margin=dict(l=12, r=12, t=56, b=8),
                      title=dict(text="Best Hour by City (highest CTR)", x=0.01, y=0.98, xanchor="left", font=dict(size=16)),
                      hovermode=False, yaxis_title="CTR (%)")
    fig.update_yaxes(tickformat=".2f",
                     range=[0, float(best_hour["CTR (%)"].max()*1.2) if not best_hour.empty else None],
                     showgrid=True, gridcolor="rgba(0,0,0,0.10)")
    return fig

gallery = [
    ("Impressions by Channel (Daily + 7-day rolling)", make_time_fig("Impressions", ",.0f", "Impressions")),
    ("Clicks by Channel (Daily + 7-day rolling)",      make_time_fig("Clicks", ",.0f", "Clicks")),
    ("CTR (%) by Channel (Daily + 7-day rolling)",     make_time_fig("CTR (%)", ".2f", "CTR (%)")),
    ("CPC (€) by Channel (Daily + 7-day rolling)",     make_time_fig("CPC (€)", ",.2f", "CPC (€)")),
    ("CTR (%) by City (weighted)",                     make_city_ctr_fig()),
    ("Clicks by City & Channel",                       make_city_clicks_fig()),
]
best_hour_fig = make_best_hour_by_city_fig()
if best_hour_fig is not None:
    gallery.append(("Best Hour by City (highest CTR)", best_hour_fig))

# 3) Gallery index + navigation buttons
if "gallery_idx" not in st.session_state:
    st.session_state.gallery_idx = 0

def nav(delta):
    n = len(gallery)
    st.session_state.gallery_idx = (st.session_state.gallery_idx + delta) % n

# Header with arrows + indicator
c_prev, c_title, c_next = st.columns([1, 6, 1])
with c_prev:
    st.button("◀︎ Prev", on_click=nav, args=(-1,), use_container_width=True)
with c_next:
    st.button("Next ▶︎", on_click=nav, args=(+1,), use_container_width=True)

title, fig = gallery[st.session_state.gallery_idx]
with c_title:
    st.markdown(f"<div class='gallery-title'>{title}</div>", unsafe_allow_html=True)
    dots = []
    for i in range(len(gallery)):
        dots.append("●" if i == st.session_state.gallery_idx else "○")
    st.markdown(f"<div class='gallery-dots'>{' '.join(dots)}</div>", unsafe_allow_html=True)

# Single chart (constant height to avoid scroll)
st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True, "displaylogo": False})

st.divider()

# =========================
# NARRATIVE — ENGLISH (clean & airy)
# =========================
st.subheader("🔎 Insights & Recommendations — Based on current filters")

def text_insights_en(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No data for the selected filters._"

    # Totals
    tot_impr = int(df["Impressions"].sum())
    tot_clk  = int(df["Clicks"].sum())
    tot_spend= float(df["Spend (€)"].sum())
    ctr_g    = (tot_clk / tot_impr * 100) if tot_impr > 0 else float("nan")
    cpc_g    = (tot_spend / tot_clk) if tot_clk > 0 else float("nan")
    cpm_g    = (tot_spend / tot_impr * 1000) if tot_impr > 0 else float("nan")

    # By channel
    ch = df.groupby("Channel", dropna=True).agg(
        Impressions=("Impressions","sum"),
        Clicks=("Clicks","sum"),
        Spend=("Spend (€)","sum")).reset_index()
    ch["CTR (%)"] = np.where(ch["Impressions"]>0, ch["Clicks"]/ch["Impressions"]*100, np.nan)
    ch["CPC (€)"] = np.where(ch["Clicks"]>0, ch["Spend"]/ch["Clicks"], np.nan)
    ch["CPM (€)"] = np.where(ch["Impressions"]>0, ch["Spend"]/ch["Impressions"]*1000, np.nan)

    best_ctr = ch.sort_values("CTR (%)", ascending=False).iloc[0] if not ch.empty else None
    best_cpc = ch.sort_values("CPC (€)", ascending=True).iloc[0] if not ch.empty else None
    best_cpm = ch.sort_values("CPM (€)", ascending=True).iloc[0] if not ch.empty else None

    # By city
    city = df.groupby("City", dropna=True).agg(
        Impressions=("Impressions","sum"),
        Clicks=("Clicks","sum"),
        Spend=("Spend (€)","sum")).reset_index()
    city["CTR (%)"] = np.where(city["Impressions"]>0, city["Clicks"]/city["Impressions"]*100, np.nan)
    city["CPC (€)"] = np.where(city["Clicks"]>0, city["Spend"]/city["Clicks"], np.nan)

    top_city_ctr = city.sort_values("CTR (%)", ascending=False).iloc[0] if not city.empty else None
    best_city_cpc= city.sort_values("CPC (€)", ascending=True).iloc[0] if not city.empty else None

    # City × Channel winners (highest CTR)
    cc = df.groupby(["City","Channel"], dropna=True).agg(
        Impressions=("Impressions","sum"), Clicks=("Clicks","sum")).reset_index()
    cc["CTR (%)"] = np.where(cc["Impressions"]>0, cc["Clicks"]/cc["Impressions"]*100, np.nan)
    winners = (cc.sort_values(["City","CTR (%)"], ascending=[True,False]).groupby("City").head(1)
               if not cc.empty else pd.DataFrame(columns=["City","Channel","CTR (%)"]))

    # Best hour (if available)
    hour_lines = []
    if "Hour" in df.columns and not df.dropna(subset=["Hour"]).empty:
        df_h = df.dropna(subset=["Hour"]).copy()
        df_h["Hour"] = df_h["Hour"].astype(int)
        city_hour = df_h.groupby(["City","Hour"]).agg(Impressions=("Impressions","sum"), Clicks=("Clicks","sum")).reset_index()
        city_hour["CTR (%)"] = np.where(city_hour["Impressions"]>0, city_hour["Clicks"]/city_hour["Impressions"]*100, np.nan)
        best_hour = (city_hour.sort_values(["City","CTR (%)"], ascending=[True,False]).groupby("City").head(1))
        for _, r in best_hour.iterrows():
            hour_lines.append(f"- **{r['City']}**: best around **{int(r['Hour']):02d}:00** (CTR **{r['CTR (%)']:.2f}%**).")

    # Helpers
    pct = lambda x: "—" if pd.isna(x) else f"{x:.2f}%"
    eur = lambda x: "—" if pd.isna(x) else f"{x:,.2f}€"
    i   = lambda x: f"{int(x):,}"

    lines = []
    lines.append(f"**Overall.** {i(tot_impr)} impressions, {i(tot_clk)} clicks → **CTR {pct(ctr_g)}**, **CPC {eur(cpc_g)}**, **CPM {eur(cpm_g)}**.")
    if best_ctr is not None and best_cpc is not None and best_cpm is not None:
        lines.append(f"**By channel.** Highest CTR on **{best_ctr['Channel']}** ({pct(best_ctr['CTR (%)'])}); "
                     f"lowest CPC on **{best_cpc['Channel']}** ({eur(best_cpc['CPC (€)'])}); "
                     f"lowest CPM on **{best_cpm['Channel']}** ({eur(best_cpm['CPM (€)'])}).")
    bits = []
    if top_city_ctr is not None: bits.append(f"top CTR in **{top_city_ctr['City']}** ({pct(top_city_ctr['CTR (%)'])})")
    if best_city_cpc is not None: bits.append(f"lowest CPC in **{best_city_cpc['City']}** ({eur(best_city_cpc['CPC (€)'])})")
    if bits: lines.append("**By city.** " + " · ".join(bits) + ".")
    if not winners.empty:
        bullets = [f"- **{r.City}** → best channel: **{r.Channel}** ({pct(r['CTR (%)'])})" for _, r in winners.iterrows()]
        lines.append("**City × channel winners:**\n" + "\n".join(bullets))
    if hour_lines:
        lines.append("**Best hours to schedule:**\n" + "\n".join(hour_lines))
    tips = []
    if best_ctr is not None and best_cpc is not None:
        tips.append(f"Shift incremental budget to **{best_ctr['Channel']}** (highest CTR) and **{best_cpc['Channel']}** (lowest CPC) in winning cities.")
    if not winners.empty:
        tips.append("Scale the city–channel pairs listed above to maximize clicks at the lowest cost.")
    tips.append("Reduce or test new creatives/targeting where CTR is low and CPC/CPM are high.")
    lines.append("**Recommendations.** " + " ".join(tips))
    return "\n\n".join(lines)

st.markdown(text_insights_en(fdf))
