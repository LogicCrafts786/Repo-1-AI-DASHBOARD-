"""
utils.py — Helper functions for AI Enterprise Dashboard
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io


# ── Colour palette ────────────────────────────────────────────────────────────
PALETTE = {
    "primary":   "#0F4C81",
    "secondary": "#00B4D8",
    "accent":    "#F77F00",
    "success":   "#2DC653",
    "danger":    "#E63946",
    "warning":   "#FFB703",
    "bg_dark":   "#0D1B2A",
    "bg_card":   "#1B2A3B",
    "text":      "#E0E8F0",
    "muted":     "#7A8FA6",
}

SEQUENTIAL   = px.colors.sequential.Blues
DIVERGING    = px.colors.diverging.RdBu
CATEGORICAL  = [
    "#00B4D8", "#F77F00", "#2DC653", "#E63946",
    "#FFB703", "#9D4EDD", "#06D6A0", "#EF476F",
]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Sans, sans-serif", color="#E0E8F0", size=12),
    title_font=dict(family="IBM Plex Sans, sans-serif", color="#E0E8F0", size=16),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.1)"),
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis=dict(gridcolor="rgba(255,255,255,0.07)", zerolinecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.07)", zerolinecolor="rgba(255,255,255,0.1)"),
)


# ── Data loading & cleaning ───────────────────────────────────────────────────

def load_data(path: str = "data/dataset.csv") -> pd.DataFrame:
    """Load dataset; generate synthetic data if file is missing."""
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        df = _generate_fallback_data()
    df = _cast_types(df)
    return df


def _cast_types(df: pd.DataFrame) -> pd.DataFrame:
    df["Date"]  = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"]  = df["Year"].astype(int)
    df["Month"] = df["Month"].astype(int)
    return df


def _generate_fallback_data() -> pd.DataFrame:
    """Synthetic 1 200-row sales dataset."""
    import random, datetime
    random.seed(42);  np.random.seed(42)
    n = 1200
    cats    = ["Electronics", "Software", "Services", "Hardware", "Consulting"]
    regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
    channels= ["Direct", "Partner", "Online", "Reseller"]
    segs    = ["Enterprise", "SMB", "Mid-Market", "Startup"]
    stats   = ["Closed Won", "Closed Lost", "In Progress", "On Hold"]
    start   = datetime.datetime(2022, 1, 1)
    dates   = [start + datetime.timedelta(days=random.randint(0, 729)) for _ in range(n)]
    cat_col = np.random.choice(cats, n, p=[0.30, 0.25, 0.20, 0.15, 0.10])
    base    = {"Electronics":15000,"Software":25000,"Services":10000,"Hardware":8000,"Consulting":30000}
    rev     = [round(base[c]*np.random.lognormal(0,0.5),2) for c in cat_col]
    cost_r  = np.random.uniform(0.4, 0.75, n)
    cost    = [round(r*c,2) for r,c in zip(rev,cost_r)]
    profit  = [round(r-c,2) for r,c in zip(rev,cost)]
    pm      = [round(p/r*100,2) for p,r in zip(profit,rev)]
    units   = [max(1,int(r/(base[c]*0.8))) for r,c in zip(rev,cat_col)]
    sat     = np.round(np.clip(np.random.normal(3.8,0.8,n),1,5),1)
    df = pd.DataFrame({
        "Deal_ID":  [f"DL-{str(i).zfill(5)}" for i in range(1,n+1)],
        "Date":     [d.strftime("%Y-%m-%d") for d in dates],
        "Year":     [d.year for d in dates],
        "Month":    [d.month for d in dates],
        "Quarter":  [f"Q{(d.month-1)//3+1}" for d in dates],
        "Region":   np.random.choice(regions,n,p=[0.35,0.25,0.20,0.12,0.08]),
        "Category": cat_col,
        "Channel":  np.random.choice(channels,n,p=[0.40,0.25,0.20,0.15]),
        "Segment":  np.random.choice(segs,n,p=[0.35,0.30,0.25,0.10]),
        "Sales_Rep":[f"Rep_{str(i).zfill(2)}" for i in np.random.randint(1,21,n)],
        "Status":   np.random.choice(stats,n,p=[0.45,0.25,0.20,0.10]),
        "Revenue":  rev, "Cost": cost, "Profit": profit,
        "Profit_Margin": pm, "Units_Sold": units,
        "Customer_Satisfaction": sat,
    })
    return df


# ── Cleaning helpers ──────────────────────────────────────────────────────────

def get_data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    report = pd.DataFrame({
        "Column":       df.columns,
        "Type":         df.dtypes.astype(str).values,
        "Non-Null":     df.notnull().sum().values,
        "Null Count":   df.isnull().sum().values,
        "Null %":       (df.isnull().mean()*100).round(2).values,
        "Unique":       df.nunique().values,
        "Sample":       [str(df[c].dropna().iloc[0]) if df[c].notna().any() else "N/A" for c in df.columns],
    })
    return report


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    original_len = len(df)
    log = {}

    # Fill numeric nulls with median
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols:
        n_null = df[col].isnull().sum()
        if n_null:
            df[col] = df[col].fillna(df[col].median())
            log[col] = f"Filled {n_null} nulls with median ({df[col].median():.2f})"

    # Fill categorical nulls with mode
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        n_null = df[col].isnull().sum()
        if n_null:
            mode_val = df[col].mode()[0]
            df[col] = df[col].fillna(mode_val)
            log[col] = f"Filled {n_null} nulls with mode ('{mode_val}')"

    # Remove duplicates
    dupes = df.duplicated().sum()
    df = df.drop_duplicates()
    if dupes:
        log["Duplicates"] = f"Removed {dupes} duplicate rows"

    log["_summary"] = f"Cleaned dataset: {original_len} → {len(df)} rows"
    return df, log


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    if filters.get("year"):
        df = df[df["Year"].isin(filters["year"])]
    if filters.get("region"):
        df = df[df["Region"].isin(filters["region"])]
    if filters.get("category"):
        df = df[df["Category"].isin(filters["category"])]
    if filters.get("status"):
        df = df[df["Status"].isin(filters["status"])]
    if filters.get("segment"):
        df = df[df["Segment"].isin(filters["segment"])]
    if filters.get("revenue_range"):
        lo, hi = filters["revenue_range"]
        df = df[(df["Revenue"] >= lo) & (df["Revenue"] <= hi)]
    return df


# ── KPI helpers ───────────────────────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    prev = df[df["Year"] == df["Year"].max() - 1]
    curr = df[df["Year"] == df["Year"].max()]

    def delta(curr_val, prev_val):
        if prev_val and prev_val != 0:
            return round((curr_val - prev_val) / abs(prev_val) * 100, 1)
        return 0.0

    total_rev      = df["Revenue"].sum()
    prev_rev       = prev["Revenue"].sum()
    curr_rev       = curr["Revenue"].sum()

    total_profit   = df["Profit"].sum()
    avg_margin     = df["Profit_Margin"].mean()
    win_rate       = (df["Status"] == "Closed Won").mean() * 100
    avg_deal       = df[df["Status"] == "Closed Won"]["Revenue"].mean()
    avg_sat        = df["Customer_Satisfaction"].mean()
    top_region     = df.groupby("Region")["Revenue"].sum().idxmax()
    top_cat        = df.groupby("Category")["Revenue"].sum().idxmax()

    return {
        "total_revenue":      total_rev,
        "total_profit":       total_profit,
        "avg_margin":         avg_margin,
        "win_rate":           win_rate,
        "avg_deal_size":      avg_deal,
        "avg_satisfaction":   avg_sat,
        "total_records":      len(df),
        "top_region":         top_region,
        "top_category":       top_cat,
        "yoy_revenue_delta":  delta(curr_rev, prev_rev),
    }


def fmt_currency(val: float, short: bool = True) -> str:
    if short:
        if val >= 1_000_000:
            return f"${val/1_000_000:.2f}M"
        if val >= 1_000:
            return f"${val/1_000:.1f}K"
    return f"${val:,.0f}"


# ── Chart builders ────────────────────────────────────────────────────────────

def _apply_layout(fig, title=""):
    layout = dict(PLOTLY_LAYOUT)
    layout["title"] = dict(text=title, font=dict(size=16, color="#E0E8F0"), x=0.02)
    fig.update_layout(**layout)
    return fig


def chart_bar_revenue_by_region(df: pd.DataFrame) -> go.Figure:
    agg = (df.groupby("Region")["Revenue"]
             .sum()
             .reset_index()
             .sort_values("Revenue", ascending=True))
    fig = go.Figure(go.Bar(
        x=agg["Revenue"], y=agg["Region"],
        orientation="h",
        marker=dict(
            color=agg["Revenue"],
            colorscale=[[0,"#1B2A3B"],[1,"#00B4D8"]],
            line=dict(width=0),
        ),
        text=[fmt_currency(v) for v in agg["Revenue"]],
        textposition="outside",
        textfont=dict(color="#E0E8F0", size=11),
    ))
    fig.update_xaxes(showticklabels=False, showgrid=False)
    return _apply_layout(fig, "Revenue by Region")


def chart_line_monthly_trend(df: pd.DataFrame) -> go.Figure:
    df2 = df.copy()
    df2["Period"] = df2["Date"].dt.to_period("M").astype(str)
    agg = (df2.groupby(["Period","Category"])["Revenue"]
              .sum()
              .reset_index()
              .sort_values("Period"))
    fig = px.line(agg, x="Period", y="Revenue", color="Category",
                  color_discrete_sequence=CATEGORICAL,
                  markers=True, line_shape="spline")
    fig.update_traces(line=dict(width=2), marker=dict(size=5))
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=10))
    return _apply_layout(fig, "Monthly Revenue Trend by Category")


def chart_pie_category(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("Category")["Revenue"].sum().reset_index()
    fig = go.Figure(go.Pie(
        labels=agg["Category"], values=agg["Revenue"],
        hole=0.52,
        marker=dict(colors=CATEGORICAL, line=dict(color="#0D1B2A", width=2)),
        textinfo="label+percent",
        textfont=dict(color="#E0E8F0", size=12),
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    ))
    fig.add_annotation(text="Revenue<br>Mix", x=0.5, y=0.5,
                       font=dict(size=14, color="#E0E8F0"), showarrow=False)
    return _apply_layout(fig, "Revenue by Category")


def chart_histogram_profit_margin(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=df["Profit_Margin"], nbinsx=30,
        marker=dict(
            color=df["Profit_Margin"],
            colorscale=[[0,"#E63946"],[0.5,"#FFB703"],[1,"#2DC653"]],
            line=dict(width=0.5, color="#0D1B2A"),
        ),
        hovertemplate="Margin: %{x:.1f}%<br>Count: %{y}<extra></extra>",
    ))
    fig.add_vline(x=df["Profit_Margin"].mean(), line_dash="dash",
                  line_color="#00B4D8", annotation_text=f"Mean: {df['Profit_Margin'].mean():.1f}%",
                  annotation_font_color="#00B4D8")
    fig.update_xaxes(title_text="Profit Margin (%)")
    fig.update_yaxes(title_text="Count")
    return _apply_layout(fig, "Profit Margin Distribution")


def chart_scatter_revenue_profit(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df, x="Revenue", y="Profit",
        color="Category", size="Units_Sold",
        hover_data=["Region", "Status", "Sales_Rep"],
        color_discrete_sequence=CATEGORICAL,
        opacity=0.75,
        size_max=22,
        trendline="ols",
    )
    fig.update_traces(marker=dict(line=dict(width=0.5, color="#0D1B2A")))
    fig.update_xaxes(title_text="Revenue ($)")
    fig.update_yaxes(title_text="Profit ($)")
    return _apply_layout(fig, "Revenue vs Profit (sized by Units Sold)")


def chart_heatmap_region_category(df: pd.DataFrame) -> go.Figure:
    pivot = df.pivot_table(
        values="Revenue", index="Region", columns="Category", aggfunc="sum"
    ).fillna(0)
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0,"#0D1B2A"],[0.5,"#0F4C81"],[1,"#00B4D8"]],
        hoverongaps=False,
        hovertemplate="Region: %{y}<br>Category: %{x}<br>Revenue: $%{z:,.0f}<extra></extra>",
        text=[[fmt_currency(v) for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(size=10, color="#E0E8F0"),
    ))
    return _apply_layout(fig, "Revenue Heatmap — Region × Category")


def chart_waterfall_quarterly(df: pd.DataFrame) -> go.Figure:
    agg = (df.groupby("Quarter")["Revenue"].sum()
             .reindex(["Q1","Q2","Q3","Q4"])
             .fillna(0))
    diffs = [agg.iloc[0]] + list(np.diff(agg.values))
    colors = ["#2DC653" if d >= 0 else "#E63946" for d in diffs]

    fig = go.Figure(go.Bar(
        x=agg.index.tolist(), y=diffs,
        marker_color=colors,
        text=[fmt_currency(abs(v)) for v in diffs],
        textposition="outside",
        textfont=dict(color="#E0E8F0"),
    ))
    fig.update_yaxes(title_text="Revenue ($)")
    return _apply_layout(fig, "Quarterly Revenue Waterfall")


# ── Export helper ─────────────────────────────────────────────────────────────

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")
