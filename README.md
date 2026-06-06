# 📊 AI Enterprise Dashboard

A production-grade, dark-themed business intelligence dashboard built with **Python**, **Streamlit**, **Plotly**, **Pandas**, and **NumPy**. Designed for enterprise sales analytics with interactive filters, KPI tracking, and rich visualizations.

---

## 🖼️ Screenshots

| Overview Tab | Deep Analysis Tab | Data & Quality Tab |
|:---:|:---:|:---:|
| KPI cards + charts | Scatter, histogram, heatmap | Quality report + export |

---

## ✨ Features

| Feature | Description |
|---|---|
| **KPI Cards** | Total Revenue, Total Profit, Win Rate, Avg Deal Size, Customer Satisfaction, Total Records |
| **Interactive Sidebar** | Filter by Year, Region, Category, Segment, Status, and Revenue Range |
| **5+ Plotly Charts** | Bar, Line, Pie (donut), Histogram, Scatter, Heatmap, Waterfall |
| **Dataset Overview** | Shape, dtypes, date range, sample values |
| **Data Cleaning** | Auto-fill nulls (median/mode), remove duplicates, full cleaning log |
| **Data Quality Report** | Null counts, unique values, type information per column |
| **Top Performers Table** | Sales rep leaderboard with revenue, margins, satisfaction |
| **Download Filtered Data** | Export as CSV from sidebar or Data tab |
| **Professional UI** | Dark theme, IBM Plex fonts, gradient header, animated cards |
| **Descriptive Statistics** | Full `describe()` on numeric columns |

---

## 📁 Folder Structure

```
AI-Dashboard/
│
├── app.py                  # Main Streamlit application
├── utils.py                # Data loading, cleaning, KPIs, chart builders
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
├── data/
│   └── dataset.csv         # 1,200-row synthetic sales dataset
│
└── assets/
    └── dashboard_screenshot.png   # (Add after first run)
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/AI-Dashboard.git
cd AI-Dashboard
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

```bash
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**.

> 💡 If `data/dataset.csv` is missing, the app auto-generates a 1,200-row synthetic dataset on startup.

---

## 📊 Dashboard Sections

### Overview Tab
- **KPI Row** — 6 metric cards with YoY delta indicators
- **Monthly Revenue Trend** — Multi-category line chart (spline)
- **Revenue by Category** — Donut pie chart
- **Revenue by Region** — Horizontal bar chart
- **Quarterly Waterfall** — Q1–Q4 revenue delta chart

### Deep Analysis Tab
- **Profit Margin Distribution** — Histogram with mean line
- **Revenue vs Profit Scatter** — Bubble chart sized by units sold, with OLS trendline
- **Region × Category Heatmap** — Cross-dimensional revenue heatmap
- **Top 10 Sales Reps** — Leaderboard table
- **Channel Performance** — Summary table with win rate and margins

### Data & Quality Tab
- **Dataset Metrics** — Row count, column count, date range
- **Data Quality Report** — Per-column null analysis
- **Cleaning Log** — Step-by-step cleaning actions taken
- **Filtered Data Preview** — Adjustable row count slider
- **Descriptive Statistics** — Full numeric summary
- **CSV Export** — Filtered dataset or full clean dataset

---

## 🎛️ Sidebar Filters

| Filter | Type | Description |
|---|---|---|
| Year | Multi-select | Filter by 2022 and/or 2023 |
| Region | Multi-select | North America, Europe, APAC, LATAM, ME |
| Category | Multi-select | Electronics, Software, Services, Hardware, Consulting |
| Segment | Multi-select | Enterprise, SMB, Mid-Market, Startup |
| Deal Status | Multi-select | Closed Won, Closed Lost, In Progress, On Hold |
| Revenue Range | Range slider | Min/max revenue filter |

---

## 🗄️ Dataset Schema

The synthetic dataset contains **1,200 rows** and **17 columns**:

| Column | Type | Description |
|---|---|---|
| `Deal_ID` | string | Unique deal identifier |
| `Date` | date | Deal close/update date |
| `Year` / `Month` / `Quarter` | int/str | Time dimensions |
| `Region` | category | Sales region |
| `Category` | category | Product/service category |
| `Channel` | category | Sales channel |
| `Segment` | category | Customer segment |
| `Sales_Rep` | string | Assigned representative |
| `Status` | category | Deal status |
| `Revenue` | float | Deal revenue in USD |
| `Cost` | float | Associated cost in USD |
| `Profit` | float | Revenue minus cost |
| `Profit_Margin` | float | Profit as % of revenue |
| `Units_Sold` | int | Number of units |
| `Customer_Satisfaction` | float | Score 1.0–5.0 |

---

## 🛠️ Technologies Used

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.10+ | Core language |
| **Streamlit** | ≥ 1.35 | Web application framework |
| **Plotly** | ≥ 5.22 | Interactive visualizations |
| **Pandas** | ≥ 2.2 | Data manipulation & analysis |
| **NumPy** | ≥ 1.26 | Numerical computing |
| **Statsmodels** | ≥ 0.14 | OLS trendlines in scatter plot |
| **OpenPyXL** | ≥ 3.1 | Excel export support |

---

## 🎨 Design System

- **Color palette**: Deep navy background (`#0D1B2A`), cyan accent (`#00B4D8`), orange secondary (`#F77F00`)
- **Typography**: IBM Plex Sans (UI) + IBM Plex Mono (numbers/code)
- **Theme**: Dark enterprise — no generic gradients, custom CSS throughout
- **Charts**: Transparent backgrounds, subtle grid lines, consistent categorical palette

---

## 🔧 Customization

- **Swap the dataset**: Replace `data/dataset.csv` with your own CSV and update column references in `utils.py`
- **Add charts**: Add a new function in `utils.py` following the `chart_*` naming convention, then call it in `app.py`
- **Change colours**: Edit the CSS variables at the top of the `<style>` block in `app.py`
- **Add filters**: Extend the `apply_filters()` function in `utils.py` and add the corresponding widget in the sidebar

---

## 📄 License

— feel free to use, modify, and distribute.

---

<div align="center">
  Built with ❤️ using Streamlit & Plotly
</div>
