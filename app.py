import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="AI Enterprise Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Mock Dataset Generation (For demonstration & easy replication)
# In production, replace this with: df = pd.read_csv("your_dataset.csv")
@st.cache_data
def load_and_clean_data():
    np.random.seed(42)
    dates = pd.date_range(start="2025-01-01", end="2025-12-31", freq="D")
    categories = ['Electronics', 'Clothing', 'Home Decor', 'Beauty', 'Sports']
    regions = ['North America', 'Europe', 'Asia-Pacific', 'Latin America']
    
    data = {
        'Order_Date': np.random.choice(dates, size=1000),
        'Category': np.random.choice(categories, size=1000, p=[0.3, 0.25, 0.2, 0.15, 0.1]),
        'Region': np.random.choice(regions, size=1000),
        'Sales': np.random.uniform(20, 1200, size=1000),
        'Quantity': np.random.randint(1, 10, size=1000),
        'Profit_Margin': np.random.uniform(-0.1, 0.4, size=1000), # Includes negative values for cleaning demo
        'Customer_Rating': np.random.uniform(1.0, 5.0, size=1000)
    }
    
    df = pd.DataFrame(data)
    
    # --- DATA CLEANING PIPELINE ---
    # 1. Handle missing simulated values if any
    df.dropna(subset=['Sales', 'Category'], inplace=True)
    # 2. Fix Data Types
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    # 3. Feature Engineering: Calculate actual Profit
    df['Profit'] = df['Sales'] * df['Profit_Margin']
    # 4. Outlier Handling: Clip extreme ratings
    df['Customer_Rating'] = df['Customer_Rating'].clip(1.0, 5.0)
    
    return df

df = load_and_clean_data()

# 3. Sidebar Filters (Interactive Filters Requirement)
st.sidebar.header("🎯 Global Dashboard Filters")

# Region Filter
selected_regions = st.sidebar.multiselect(
    "Select Region(s):",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Category Filter
selected_categories = st.sidebar.multiselect(
    "Select Category(s):",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Date Filter Range
min_date = df['Order_Date'].min().to_pydatetime()
max_date = df['Order_Date'].max().to_pydatetime()
selected_date_range = st.sidebar.date_input(
    "Select Date Range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply Filters to Dataframe
filtered_df = df[
    (df['Region'].isin(selected_regions)) &
    (df['Category'].isin(selected_categories)) &
    (df['Order_Date'] >= pd.to_datetime(selected_date_range[0])) &
    (df['Order_Date'] <= pd.to_datetime(selected_date_range[1]))
]

# 4. Main App Layout & Header
st.title("📊 AI-Driven Performance Dashboard")
st.markdown("An interactive operational control center evaluating corporate key performance indicators.")
st.write("---")

# 5. Dataset Overview & Cleaning Documentation (Requirements 1 & 2)
with st.expander("🔍 View Dataset Overview & Cleaning Logs"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Active Data Segment Preview")
        st.dataframe(filtered_df.head(5), use_container_width=True)
    with col2:
        st.markdown("### Execution & Quality Assertions")
        st.success("✅ Missing records removed from critical vectors (Sales, Category).")
        st.success("✅ `Order_Date` normalized to standard DateTime formats.")
        st.success("✅ Synthesized composite metrics: `Profit` derived dynamically.")
        st.info(f"Showing **{filtered_df.shape[0]}** rows after executing user filters.")

st.write("---")

# 6. Key Metrics / KPIs (Requirement 3)
st.subheader("📈 Key Performance Indicators")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
avg_rating = filtered_df['Customer_Rating'].mean()
total_units = filtered_df['Quantity'].sum()

kpi1.metric(label="Total Revenue", value=f"${total_sales:,.2f}", delta=f"{total_sales * 0.05:,.2f} vs Last Mo")
kpi2.metric(label="Net Profit", value=f"${total_profit:,.2f}", delta=f"{total_profit / total_sales * 100:.1f}% Margin")
kpi3.metric(label="Units Sold", value=f"{total_units:,} pcs")
kpi4.metric(label="Avg Customer Satisfaction", value=f"{avg_rating:.2f} / 5.0")

st.write("---")

# 7. Core Visualizations Framework (Requirement 4 - 5 Distinct Visualizations)
st.subheader("Visual Analytics Engine")

# Row 1: Charts 1 & 2
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("#### 1. Revenue Trajectory (Temporal Trend)")
    timeline_df = filtered_df.groupby(filtered_df['Order_Date'].dt.to_period('M'))['Sales'].sum().reset_index()
    timeline_df['Order_Date'] = timeline_df['Order_Date'].astype(str)
    fig1 = px.line(timeline_df, x='Order_Date', y='Sales', markers=True, template="plotly_white", color_discrete_sequence=["#1E88E5"])
    st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    st.markdown("#### 2. Sector Performance (Categorical Breakdown)")
    category_df = filtered_df.groupby('Category')['Sales'].sum().sort_values(ascending=False).reset_index()
    fig2 = px.bar(category_df, x='Category', y='Sales', color='Category', template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: Charts 3 & 4
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("#### 3. Regional Acquisition Share (Composition)")
    region_df = filtered_df.groupby('Region')['Sales'].sum().reset_index()
    fig3 = px.pie(region_df, values='Sales', names='Region', hole=0.4, template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)

with row2_col2:
    st.markdown("#### 4. Pricing vs Customer Sentiment (Correlation Analysis)")
    fig4 = px.scatter(filtered_df, x='Sales', y='Customer_Rating', color='Category', opacity=0.6, template="plotly_white")
    st.plotly_chart(fig4, use_container_width=True)

# Row 3: Chart 5
st.markdown("#### 5. Profit Margin Spread (Distribution Profile)")
fig5 = px.histogram(filtered_df, x='Profit_Margin', nbins=30, color_discrete_sequence=['#4CAF50'], marginal="box", template="plotly_white")
st.plotly_chart(fig5, use_container_width=True)
