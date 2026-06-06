"""
app.py — AI Enterprise Dashboard
A professional, dark-themed Streamlit dashboard for business sales analytics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

from utils import (
    load_data, get_data_quality_report, clean_data, apply_filters,
    compute_kpis, fmt_currency, df_to_csv_bytes,
    chart_bar_revenue_by_region, chart_line_monthly_trend,
    chart_pie_category, chart_histogram_profit_margin,
    chart_scatter_revenue_profit, chart_heatmap_region_category,
    chart_waterfall_quarterly,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Enterprise Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Google fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

  /* ── Root variables ── */
  :root {
    --bg:        #0D1B2A;
    --bg-card:   #1B2A3B;
    --bg-card2:  #162232;
    --primary:   #0F4C81;
    --accent:    #00B4D8;
    --accent2:   #F77F00;
    --success:   #2DC653;
    --danger:    #E63946;
    --warning:   #FFB703;
    --text:      #E0E8F0;
    --muted:     #7A8FA6;
    --border:    rgba(0, 180, 216, 0.15);
    --radius:    12px;
  }

  /* ── Global reset ── */
  html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
  }

  .main .block-container { padding: 1.5rem 2rem 3rem; max-width: 1600px; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: #111E2C !important;
    border-right: 1px solid var(--border);
  }
  [data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--accent) !important;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 1.2rem;
    margin-bottom: 0.4rem;
  }

  /* ── Header banner ── */
  .dash-header {
    background: linear-gradient(135deg, #0F4C81 0%, #062D52 60%, #0D1B2A 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
  }
  .dash-header::before {
    content: '';
    position: absolute; top: 0; right: 0;
    width: 340px; height: 100%;
    background: radial-gradient(ellipse at top right, rgba(0,180,216,0.18) 0%, transparent 70%);
  }
  .dash-header h1 {
    font-size: 1.9rem; font-weight: 700;
    color: var(--text) !important; margin: 0; line-height: 1.2;
  }
  .dash-header h1 span { color: var(--accent); }
  .dash-header p { color: var(--muted); font-size: 0.9rem; margin: 0.3rem 0 0; }
  .dash-badge {
    background: rgba(0,180,216,0.12);
    border: 1px solid rgba(0,180,216,0.4);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.75rem;
    color: var(--accent);
    font-weight: 500;
    letter-spacing: 0.05em;
  }

  /* ── Section label ── */
  .section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 1.8rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }

  /* ── KPI cards ── */
  .kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }
  .kpi-card:hover { border-color: rgba(0,180,216,0.35); }
  .kpi-card::before {
    content: ''; position: absolute;
    bottom: 0; left: 0; right: 0; height: 3px;
    border-radius: 0 0 var(--radius) var(--radius);
  }
  .kpi-card.blue::before   { background: var(--accent); }
  .kpi-card.orange::before { background: var(--accent2); }
  .kpi-card.green::before  { background: var(--success); }
  .kpi-card.red::before    { background: var(--danger); }
  .kpi-card.yellow::before { background: var(--warning); }
  .kpi-card.purple::before { background: #9D4EDD; }

  .kpi-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    display: block;
  }
  .kpi-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.3rem;
  }
  .kpi-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--text);
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1.1;
  }
  .kpi-delta {
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 0.4rem;
    font-family: 'IBM Plex Mono', monospace;
  }
  .kpi-delta.pos { color: var(--success); }
  .kpi-delta.neg { color: var(--danger); }
  .kpi-delta.neu { color: var(--muted); }

  /* ── Chart cards ── */
  .chart-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    margin-bottom: 1rem;
  }

  /* ── Dataframe ── */
  .stDataFrame { border-radius: var(--radius) !important; }
  [data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }

  /* ── Multiselect / slider tweaks ── */
  .stMultiSelect [data-baseweb="tag"] { background: rgba(0,180,216,0.2) !important; border: none !important; }
  .stSlider [data-testid="stThumb"] { background: var(--accent) !important; }

  /* ── Expander ── */
  .streamlit-expanderHeader {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-weight: 500;
  }

  /* ── Download button ── */
  .stDownloadButton > button {
    background: rgba(0,180,216,0.12) !important;
    border: 1px solid rgba(0,180,216,0.4) !important;
    color: var(--accent) !important;
    border-radius: 8px !important;
    font-weight: 500;
    font-family: 'IBM Plex Sans', sans-serif;
    transition: background 0.2s;
  }
  .stDownloadButton > button:hover {
    background: rgba(0,180,216,0.25) !important;
  }

  /* ── Success / info alerts ── */
  .stAlert { border-radius: var(--radius) !important; }

  /* ── Tab styling ── */
  .stTabs [data-baseweb="tab-list"] { gap: 4px; background: var(--bg-card2); border-radius: var(--radius); padding: 4px; }
  .stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: var(--muted) !important;
    font-weight: 500;
    font-size: 0.85rem;
  }
  .stTabs [aria-selected="true"] {
    background: var(--primary) !important;
    color: var(--text) !important;
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Session state & data loading ──────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_raw_data():
    return load_data("data/dataset.csv")

@st.cache_data(show_spinner=False)
def get_cleaned_data(raw_df):
    df, log = clean_data(raw_df.copy())
    return df, log

if "raw_df" not in st.session_state:
    with st.spinner("Loading dataset…"):
        st.session_state.raw_df = get_raw_data()
    st.session_state.df, st.session_state.clean_log = get_cleaned_data(st.session_state.raw_df)

raw_df   = st.session_state.raw_df
df_clean = st.session_state.df
clean_log= st.session_state.clean_log


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem; text-align:center;">
        <div style="font-size:2rem;">📊</div>
        <div style="font-weight:700; font-size:1rem; color:#E0E8F0;">AI Enterprise</div>
        <div style="font-size:0.7rem; color:#7A8FA6; letter-spacing:0.1em;">DASHBOARD v1.0</div>
    </div>
    <hr style="border-color:rgba(0,180,216,0.15); margin:0.5rem 0 1rem;">
    """, unsafe_allow_html=True)

    st.markdown("### 📅 Time")
    years = sorted(df_clean["Year"].unique())
    sel_years = st.multiselect("Year", years, default=years)

    st.markdown("### 🌍 Geography")
    regions = sorted(df_clean["Region"].unique())
    sel_regions = st.multiselect("Region", regions, default=regions)

    st.markdown("### 🏷️ Business")
    categories = sorted(df_clean["Category"].unique())
    sel_cats = st.multiselect("Category", categories, default=categories)

    segments = sorted(df_clean["Segment"].unique())
    sel_segs = st.multiselect("Segment", segments, default=segments)

    statuses = sorted(df_clean["Status"].unique())
    sel_status = st.multiselect("Deal Status", statuses, default=statuses)

    st.markdown("### 💰 Revenue Range")
    rev_min = float(df_clean["Revenue"].min())
    rev_max = float(df_clean["Revenue"].max())
    rev_range = st.slider(
        "Revenue ($)", min_value=rev_min, max_value=rev_max,
        value=(rev_min, rev_max), format="$%,.0f"
    )

    st.markdown("---")
    # Download button in sidebar
    filtered_for_dl = apply_filters(df_clean, {
        "year": sel_years, "region": sel_regions, "category": sel_cats,
        "status": sel_status, "segment": sel_segs, "revenue_range": rev_range,
    })
    st.download_button(
        label="⬇️  Export Filtered Data",
        data=df_to_csv_bytes(filtered_for_dl),
        file_name=f"dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown(f"<div style='text-align:center;font-size:0.7rem;color:#7A8FA6;margin-top:0.5rem;'>{len(filtered_for_dl):,} records selected</div>", unsafe_allow_html=True)


# ── Apply filters ─────────────────────────────────────────────────────────────
df = apply_filters(df_clean, {
    "year": sel_years, "region": sel_regions, "category": sel_cats,
    "status": sel_status, "segment": sel_segs, "revenue_range": rev_range,
})

if df.empty:
    st.warning("⚠️ No data matches the selected filters. Please adjust your sidebar selections.")
    st.stop()

kpis = compute_kpis(df)


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
  <div>
    <h1>AI Enterprise <span>Dashboard</span></h1>
    <p>Business sales analytics · {len(df):,} records · Last updated {datetime.now().strftime("%b %d, %Y %H:%M")}</p>
  </div>
  <div>
    <span class="dash-badge">● LIVE</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── TABS ──────────────────────────────────────────────────────────────────────
tab_overview, tab_analysis, tab_data = st.tabs([
    "📈  Overview", "🔬  Deep Analysis", "🗃️  Data & Quality"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab_overview:

    # ── KPI row ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Key Performance Indicators</div>', unsafe_allow_html=True)

    def kpi_delta_html(val, suffix="%"):
        if val > 0:
            return f'<div class="kpi-delta pos">▲ +{val:.1f}{suffix} YoY</div>'
        elif val < 0:
            return f'<div class="kpi-delta neg">▼ {val:.1f}{suffix} YoY</div>'
        return f'<div class="kpi-delta neu">— N/A YoY</div>'

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    with k1:
        st.markdown(f"""<div class="kpi-card blue">
            <span class="kpi-icon">💵</span>
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">{fmt_currency(kpis['total_revenue'])}</div>
            {kpi_delta_html(kpis['yoy_revenue_delta'])}
        </div>""", unsafe_allow_html=True)

    with k2:
        st.markdown(f"""<div class="kpi-card green">
            <span class="kpi-icon">📈</span>
            <div class="kpi-label">Total Profit</div>
            <div class="kpi-value">{fmt_currency(kpis['total_profit'])}</div>
            <div class="kpi-delta neu">Avg margin {kpis['avg_margin']:.1f}%</div>
        </div>""", unsafe_allow_html=True)

    with k3:
        st.markdown(f"""<div class="kpi-card orange">
            <span class="kpi-icon">🎯</span>
            <div class="kpi-label">Win Rate</div>
            <div class="kpi-value">{kpis['win_rate']:.1f}%</div>
            <div class="kpi-delta neu">Closed Won deals</div>
        </div>""", unsafe_allow_html=True)

    with k4:
        st.markdown(f"""<div class="kpi-card yellow">
            <span class="kpi-icon">🤝</span>
            <div class="kpi-label">Avg Deal Size</div>
            <div class="kpi-value">{fmt_currency(kpis['avg_deal_size'])}</div>
            <div class="kpi-delta neu">Won deals only</div>
        </div>""", unsafe_allow_html=True)

    with k5:
        star = "⭐" if kpis['avg_satisfaction'] >= 4 else "🌟"
        st.markdown(f"""<div class="kpi-card purple">
            <span class="kpi-icon">{star}</span>
            <div class="kpi-label">Avg Satisfaction</div>
            <div class="kpi-value">{kpis['avg_satisfaction']:.2f}<span style="font-size:1rem;color:#7A8FA6"> /5</span></div>
            <div class="kpi-delta neu">Customer score</div>
        </div>""", unsafe_allow_html=True)

    with k6:
        st.markdown(f"""<div class="kpi-card red">
            <span class="kpi-icon">📋</span>
            <div class="kpi-label">Total Records</div>
            <div class="kpi-value">{kpis['total_records']:,}</div>
            <div class="kpi-delta neu">Top: {kpis['top_region'][:12]}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)

    # ── Charts row 1 ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Revenue Analysis</div>', unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(chart_line_monthly_trend(df), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(chart_pie_category(df), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Charts row 2 ─────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(chart_bar_revenue_by_region(df), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(chart_waterfall_quarterly(df), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DEEP ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_analysis:

    st.markdown('<div class="section-label">Profit & Efficiency Analysis</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(chart_histogram_profit_margin(df), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(chart_scatter_revenue_profit(df), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Cross-Dimensional Heatmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(chart_heatmap_region_category(df), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Top performers table ──────────────────────────────────────────────────
    st.markdown('<div class="section-label">Top 10 Sales Representatives</div>', unsafe_allow_html=True)
    top_reps = (
        df[df["Status"] == "Closed Won"]
        .groupby("Sales_Rep")
        .agg(
            Deals=("Deal_ID", "count"),
            Revenue=("Revenue", "sum"),
            Avg_Deal=("Revenue", "mean"),
            Avg_Margin=("Profit_Margin", "mean"),
            Avg_Sat=("Customer_Satisfaction", "mean"),
        )
        .round(2)
        .sort_values("Revenue", ascending=False)
        .head(10)
        .reset_index()
    )
    top_reps["Revenue"]   = top_reps["Revenue"].apply(fmt_currency)
    top_reps["Avg_Deal"]  = top_reps["Avg_Deal"].apply(fmt_currency)
    top_reps["Avg_Margin"]= top_reps["Avg_Margin"].apply(lambda x: f"{x:.1f}%")
    top_reps["Avg_Sat"]   = top_reps["Avg_Sat"].apply(lambda x: f"{x:.2f} ⭐")
    top_reps.columns      = ["Sales Rep","Deals","Revenue","Avg Deal","Avg Margin","Avg Satisfaction"]
    st.dataframe(top_reps, use_container_width=True, hide_index=True)

    # ── Channel breakdown ─────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Channel Performance Summary</div>', unsafe_allow_html=True)
    ch_agg = (
        df.groupby("Channel")
        .agg(
            Records=("Deal_ID","count"),
            Revenue=("Revenue","sum"),
            Profit=("Profit","sum"),
            Win_Rate=("Status", lambda x: (x=="Closed Won").mean()*100),
            Avg_Margin=("Profit_Margin","mean"),
        )
        .round(2)
        .sort_values("Revenue", ascending=False)
        .reset_index()
    )
    ch_agg["Revenue"]    = ch_agg["Revenue"].apply(fmt_currency)
    ch_agg["Profit"]     = ch_agg["Profit"].apply(fmt_currency)
    ch_agg["Win_Rate"]   = ch_agg["Win_Rate"].apply(lambda x: f"{x:.1f}%")
    ch_agg["Avg_Margin"] = ch_agg["Avg_Margin"].apply(lambda x: f"{x:.1f}%")
    ch_agg.columns       = ["Channel","Records","Revenue","Profit","Win Rate","Avg Margin"]
    st.dataframe(ch_agg, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DATA & QUALITY
# ═══════════════════════════════════════════════════════════════════════════════
with tab_data:

    # ── Dataset overview ──────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Dataset Overview</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows",    f"{len(raw_df):,}")
    m2.metric("Total Columns", f"{len(raw_df.columns)}")
    m3.metric("Date Range",    f"{raw_df['Year'].min()} – {raw_df['Year'].max()}")
    m4.metric("After Cleaning",f"{len(df_clean):,}")

    # ── Data quality report ───────────────────────────────────────────────────
    st.markdown('<div class="section-label">Data Quality Report (Raw)</div>', unsafe_allow_html=True)
    quality_report = get_data_quality_report(raw_df)
    st.dataframe(quality_report, use_container_width=True, hide_index=True)

    # ── Cleaning log ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Cleaning Log</div>', unsafe_allow_html=True)
    with st.expander("View detailed cleaning steps", expanded=True):
        if clean_log:
            for col, msg in clean_log.items():
                icon = "✅" if "summary" not in col else "🔧"
                st.markdown(f"**{icon} `{col}`** — {msg}")
        else:
            st.success("No cleaning required — dataset is pristine!")

    # ── Filtered data preview ─────────────────────────────────────────────────
    st.markdown('<div class="section-label">Filtered Data Preview</div>', unsafe_allow_html=True)
    st.info(f"Showing **{len(df):,}** records matching current filters.")

    n_show = st.slider("Rows to preview", 10, min(200, len(df)), 25, step=5)
    st.dataframe(df.head(n_show), use_container_width=True, hide_index=True)

    # ── Descriptive statistics ────────────────────────────────────────────────
    st.markdown('<div class="section-label">Descriptive Statistics</div>', unsafe_allow_html=True)
    num_cols = ["Revenue","Cost","Profit","Profit_Margin","Units_Sold","Customer_Satisfaction"]
    desc = df[num_cols].describe().round(2)
    st.dataframe(desc, use_container_width=True)

    # ── Download section ──────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Export Data</div>', unsafe_allow_html=True)
    dl1, dl2, _ = st.columns([1, 1, 2])

    with dl1:
        st.download_button(
            label="⬇️  Filtered Dataset",
            data=df_to_csv_bytes(df),
            file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl2:
        st.download_button(
            label="⬇️  Full Clean Dataset",
            data=df_to_csv_bytes(df_clean),
            file_name=f"clean_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:rgba(0,180,216,0.1); margin:2rem 0 1rem;">
<div style="text-align:center; color:#7A8FA6; font-size:0.75rem; padding-bottom:1rem;">
  AI Enterprise Dashboard · Built with Streamlit, Plotly & Pandas
  · <span style="color:#00B4D8;">Data refreshes on filter change</span>
</div>
""", unsafe_allow_html=True)
