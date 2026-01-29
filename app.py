import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Strategic Intervention Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
        /* Hide Streamlit default styling */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Professional Font & Padding */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
        
        /* Metric Cards Styling */
        div[data-testid="stMetric"] {
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('dashboard_data.csv')
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("Data source not found. Please ensure 'dashboard_data.csv' is in the repository.")
    st.stop()

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Control Panel")
    st.markdown("---")
    
    # District Slicer
    all_districts = sorted(df['district_name'].unique())
    selected_districts = st.multiselect(
        "Select Target Districts",
        options=all_districts,
        default=all_districts, # Default to ALL for better initial view
        help="Select one or multiple districts to filter the dashboard."
    )
    
    if not selected_districts:
        st.warning("Please select at least one district.")
        st.stop()
        
    st.markdown("---")
    st.caption("Dashboard v2.0 | Strategic Planning Unit")

# Filter Data
df_filtered = df[df['district_name'].isin(selected_districts)]

# --- MAIN DASHBOARD ---
st.title("Strategic Support & Intervention Overview")
st.markdown("### Regional Performance & Resource Allocation")
st.markdown("---")

# --- TOP LEVEL METRICS ---
total_interventions = df_filtered['Beneficiary_Count'].sum()
top_district_name = df_filtered.groupby('district_name')['Beneficiary_Count'].sum().idxmax()
top_district_val = df_filtered.groupby('district_name')['Beneficiary_Count'].sum().max()
active_blocks = df_filtered['block_name'].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Interventions", f"{total_interventions:,.0f}")
c2.metric("Highest Demand District", top_district_name, f"{top_district_val:,.0f} reqs")
c3.metric("Active Blocks", active_blocks)
c4.metric("Support Categories", df_filtered['broad_category'].nunique())

st.markdown("<br>", unsafe_allow_html=True)

# --- TABS FOR ORGANIZED VIEW ---
tab1, tab2 = st.tabs(["📊 Executive Summary", "📍 District Deep Dive"])

# --- TAB 1: EXECUTIVE SUMMARY ---
with tab1:
    col_left, col_right = st.columns((2, 1))
    
    with col_left:
        st.subheader("Support Type Distribution (Top 15)")
        
        support_counts = df_filtered.groupby('typeofsupport')['Beneficiary_Count'].sum().nlargest(15).reset_index()
        support_counts = support_counts.sort_values('Beneficiary_Count', ascending=True)
        
        fig_bar = px.bar(
            support_counts,
            x='Beneficiary_Count',
            y='typeofsupport',
            orientation='h',
            text='Beneficiary_Count',
            color='Beneficiary_Count',
            color_continuous_scale='Blues'
        )
        
        fig_bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_bar.update_layout(
            plot_bgcolor="white",
            xaxis_title="Number of Beneficiaries",
            yaxis_title=None,
            height=500,
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("Broad Category Share")
        
        cat_counts = df_filtered.groupby('broad_category')['Beneficiary_Count'].sum().reset_index()
        
        # Professional Pie Chart (Donut Style)
        fig_pie = px.pie(
            cat_counts,
            values='Beneficiary_Count',
            names='broad_category',
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 2: DISTRICT DEEP DIVE ---
with tab2:
    st.subheader("District-wise Demand Analysis")
    st.markdown("Compare total interventions across selected districts.")
    
    # Group by District
    district_data = df_filtered.groupby('district_name')['Beneficiary_Count'].sum().reset_index()
    district_data = district_data.sort_values('Beneficiary_Count', ascending=False)
    
    # Highlight the top district
    colors = ['#1f77b4'] * len(district_data)
    colors[0] = '#d62728' # Make the top bar red for emphasis
    
    fig_dist = px.bar(
        district_data,
        x='district_name',
        y='Beneficiary_Count',
        color='Beneficiary_Count',
        color_continuous_scale='Teal' # Professional gradient
    )
    
    fig_dist.update_layout(
        plot_bgcolor="white",
        xaxis_title="District",
        yaxis_title="Total Requests",
        hovermode="x unified"
    )
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Detailed Data Table
    with st.expander("View Raw Data Table"):
        st.dataframe(
            df_filtered.groupby(['district_name', 'typeofsupport'])['Beneficiary_Count'].sum().reset_index(),
            use_container_width=True
        )
