import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dashboard_generator import DashboardGenerator
from datetime import datetime

def main():
    st.set_page_config(
        page_title="Ergosign Topic Gap Analysis Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Ergosign Topic Gap Analysis Dashboard")
    
    # Initialize dashboard generator
    generator = DashboardGenerator()
    
    # Sidebar controls
    st.sidebar.header("Dashboard Controls")
    
    # Generate new analysis button
    if st.sidebar.button("🔄 Generate New Analysis", type="primary"):
        with st.spinner("Generating new analysis..."):
            try:
                folder = generator.generate_dashboard_data()
                st.sidebar.success(f"Analysis generated: {folder}")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")
    
    # Dashboard selection
    available_dashboards = generator.get_available_dashboards()
    
    if not available_dashboards:
        st.warning("No dashboard data available. Generate a new analysis first.")
        return
    
    selected_dashboard = st.sidebar.selectbox(
        "Select Dashboard",
        options=[folder for folder, _ in available_dashboards],
        format_func=lambda x: next(display for folder, display in available_dashboards if folder == x),
        index=0
    )
    
    # Load and display dashboard
    try:
        data = generator.load_dashboard_data(selected_dashboard)
        display_dashboard(data)
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

def display_dashboard(data):
    """Display the dashboard using the loaded data."""
    
    # Header with last updated info
    st.markdown(f"""
    <div style='background-color: #2E3440; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: white; margin: 0;'>🏢 ERGOSIGN TOPIC GAP ANALYSIS DASHBOARD</h2>
        <p style='color: #D8DEE9; margin: 5px 0 0 0;'>Last Updated: {datetime.fromisoformat(data['metadata']['timestamp']).strftime('%Y-%m-%d')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🏢 COMPANIES",
            data['summary_metrics']['companies_analyzed'],
            "Analyzed"
        )
    
    with col2:
        st.metric(
            "📋 TOPICS", 
            data['summary_metrics']['topics_identified'],
            "Identified"
        )
    
    with col3:
        st.metric(
            "⚠️ GAPS",
            data['summary_metrics']['gap_opportunities'], 
            "Opportunities"
        )
    
    with col4:
        st.metric(
            "📊 COVERAGE",
            f"{data['summary_metrics']['coverage_percentage']}%",
            "Complete"
        )
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Topics Distribution Donut Chart
        st.subheader("Topics Distribution")
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=['Ergosign', 'Competitors'],
            values=[data['topic_distribution']['ergosign_percentage'], 
                   data['topic_distribution']['competitor_percentage']],
            hole=0.4,
            marker_colors=['#5E81AC', '#BF616A']
        )])
        
        fig_donut.update_layout(
            showlegend=True,
            height=300,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)
        st.caption("[Donut Chart Visual]")
    
    with col2:
        # Topics by Company Bar Chart
        st.subheader("Topics by Company")
        
        companies = list(data['topics_by_company'].keys())
        topic_counts = list(data['topics_by_company'].values())
        
        fig_bar = go.Figure(data=[
            go.Bar(
                x=companies,
                y=topic_counts,
                marker_color=['#5E81AC' if 'ergosign' in comp.lower() else '#D8DEE9' for comp in companies]
            )
        ])
        
        fig_bar.update_layout(
            height=300,
            margin=dict(t=0, b=0, l=0, r=0),
            xaxis_title="",
            yaxis_title=""
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Gap Opportunities Priority
    st.subheader("Gap Opportunities Priority")
    
    gap_data = []
    for gap in data['gap_analysis']['high_priority']:
        gap_data.append({'Priority': 'High Priority', 'Count': 1})
    for gap in data['gap_analysis']['medium_priority']:
        gap_data.append({'Priority': 'Medium Priority', 'Count': 1})
    
    if gap_data:
        gap_df = pd.DataFrame(gap_data)
        gap_summary = gap_df.groupby('Priority')['Count'].sum().reset_index()
        
        fig_gaps = go.Figure(data=[
            go.Bar(
                x=gap_summary['Priority'],
                y=gap_summary['Count'],
                text=gap_summary['Count'],
                textposition='auto',
                marker_color=['#D08770', '#EBCB8B']
            )
        ])
        
        fig_gaps.update_layout(
            height=200,
            margin=dict(t=0, b=0, l=0, r=0),
            xaxis_title="",
            yaxis_title=""
        )
        
        st.plotly_chart(fig_gaps, use_container_width=True)
    else:
        st.info("No gap opportunities identified")
    
    # Detailed data in expanders
    with st.expander("📋 Detailed Topic Analysis"):
        tab1, tab2, tab3 = st.tabs(["Company Topics", "Gap Analysis", "Coverage Analysis"])
        
        with tab1:
            for company, topics in data['detailed_data']['company_topics'].items():
                st.write(f"**{company.title()}** ({len(topics)} topics)")
                st.write(", ".join(topics))
                st.write("")
        
        with tab2:
            if data['detailed_data']['gap_topics']:
                st.write("**High Priority Gaps:**")
                for gap in data['gap_analysis']['high_priority']:
                    st.write(f"• {gap}")
                
                if data['gap_analysis']['medium_priority']:
                    st.write("**Medium Priority Gaps:**")
                    for gap in data['gap_analysis']['medium_priority']:
                        st.write(f"• {gap}")
            else:
                st.info("No gaps identified - full topic coverage achieved!")
        
        with tab3:
            if data['detailed_data']['coverage_topics']:
                st.write("**Topics covered by Ergosign:**")
                for topic in data['detailed_data']['coverage_topics']:
                    st.write(f"• {topic}")
            else:
                st.info("No topic overlap found")

if __name__ == "__main__":
    main()