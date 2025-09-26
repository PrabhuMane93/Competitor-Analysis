# Ergosign Topic Gap Analysis Dashboard

## 🎯 Overview

This dashboard recreates the exact analysis shown in your image, with persistent data storage for historical comparisons.

## 🚀 Quick Start

1. **Launch dashboard:**
   ```bash
   python run_dashboard.py
   ```
   
   Or directly:
   ```bash
   streamlit run streamlit_dashboard.py
   ```

## 📊 Dashboard Features

### Main Dashboard
- **Executive Overview**: Companies analyzed, topics identified, gaps, coverage percentage
- **Topics Distribution**: Donut chart showing Ergosign vs Competitors
- **Topics by Company**: Bar chart with topic counts per company
- **Gap Opportunities Priority**: High/Medium priority gaps visualization

### Data Persistence
- Each analysis creates a timestamped folder in `dashboards/`
- Dropdown menu to select previous analyses
- Data stored in multiple formats (JSON, CSV, TXT)

## 🔄 Generating New Analysis

Click "Generate New Analysis" button to:
1. Extract topics from CSV files in `data/` folder
2. Analyze gaps and coverage
3. Create timestamped dashboard data
4. Save to `dashboards/analysis_YYYYMMDD_HHMMSS/`

## 📁 Data Structure

Each dashboard folder contains:
- `dashboard_data.json` - Complete analysis data
- `summary_metrics.csv` - Key metrics
- `topics_by_company.csv` - Company topic breakdown
- `gap_opportunities.csv` - Gap analysis with priorities
- `analysis_info.txt` - Metadata and timestamp

## 🎨 Dashboard Recreation

The dashboard exactly matches your image with:
- Same color scheme and layout
- Identical metrics and visualizations
- Executive overview format
- Gap priority analysis

## 📋 Requirements

- Python 3.8+
- Streamlit
- Plotly
- Pandas
- Existing topic extraction system