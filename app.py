import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Strategic Intervention Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-bottom: 2rem;}
        div[data-testid="stMetric"] {
            background-color: #f8f9fa; border: 1px solid #e0e0e0;
            padding: 10px; border-radius: 5px; text-align: center;
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
    
    # 1. Select All Checkbox
    all_districts = sorted(df['district_name'].unique())
    
    # "Select All" Logic
    container = st.container()
    all_selected = st.checkbox("Select All Districts", value=True)
    
    if all_selected:
        selected_districts = container.multiselect(
            "Select Target Districts",
            options=all_districts,
            default=all_districts,
            disabled=True # Disable to prevent unselecting while "All" is checked
        )
    else:
        selected_districts = container.multiselect(
            "Select Target Districts",
            options=all_districts,
            default=all_districts[:1] # Default to first one if unchecked
        )
    
    if not selected_districts:
        st.warning("Please select at least one district.")
        st.stop()
        
    st.markdown("---")
    st.caption("Dashboard v2.1 | Strategic Planning Unit")

# Filter Data
df_filtered = df[df['district_name'].isin(selected_districts)]

# --- MAIN DASHBOARD ---
st.title("Demands by each district of Chattisgarh")
st.markdown("### District Wise Resource Demands")
st.markdown("---")

# --- TOP LEVEL METRICS ---
total_interventions = df_filtered['Beneficiary_Count'].sum()
top_district_name = df_filtered.groupby('district_name')['Beneficiary_Count'].sum().idxmax()
top_district_val = df_filtered.groupby('district_name')['Beneficiary_Count'].sum().max()
active_blocks = df_filtered['block_name'].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Interventions", f"{total_interventions:,.0f}")
c2.metric("Highest Demand District", top_district_name, f"{top_district_val:,.0f} reqs")
c3.metric("Blocks", active_blocks)
c4.metric("Support Categories", df_filtered['broad_category'].nunique())

st.markdown("<br>", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["Executive Summary", "District Deep Dive", "Support Categories"])

# --- TAB 1: EXECUTIVE SUMMARY ---
with tab1:
    col_left, col_right = st.columns((2, 1))
    
    with col_left:
        st.subheader("Specific Support Type Demand (Top 15)")
        
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
        fig_bar.update_layout(plot_bgcolor="white", xaxis_title="Beneficiaries", yaxis_title=None, height=500, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("Broad Category Share")
        cat_counts = df_filtered.groupby('broad_category')['Beneficiary_Count'].sum().reset_index()
        
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
    
    district_data = df_filtered.groupby('district_name')['Beneficiary_Count'].sum().reset_index()
    district_data = district_data.sort_values('Beneficiary_Count', ascending=False)
    
    fig_dist = px.bar(
        district_data,
        x='district_name',
        y='Beneficiary_Count',
        color='Beneficiary_Count',
        color_continuous_scale='Teal'
    )
    fig_dist.update_layout(plot_bgcolor="white", xaxis_title="District", yaxis_title="Total Requests", hovermode="x unified")
    st.plotly_chart(fig_dist, use_container_width=True)

# --- TAB 3: SUPPORT CATEGORIES (NEW) ---
with tab3:
    st.subheader("Breakdown by Category of Support")
    st.markdown("Analysis of major support buckets (Equipment, Infrastructure, Inputs, etc.)")
    
    # Check if 'categoryofsupport' exists in the data (Column F from your original Excel)
    # The column name might be 'categoryofsupport' or similar based on the cleaning script
    target_col = 'categoryofsupport' 
    
    # Fallback search for the column if name varies slightly
    if target_col not in df_filtered.columns:
        # Try to find a column that looks similar
        potential_matches = [c for c in df_filtered.columns if 'category' in c.lower() and 'broad' not in c.lower()]
        if potential_matches:
            target_col = potential_matches[0]
    
    if target_col in df_filtered.columns:
        cat_support_data = df_filtered.groupby(target_col)['Beneficiary_Count'].sum().reset_index()
        cat_support_data = cat_support_data.sort_values('Beneficiary_Count', ascending=False)
        
        # Treemap for a professional hierarchical view
        fig_tree = px.treemap(
            cat_support_data,
            path=[target_col],
            values='Beneficiary_Count',
            color='Beneficiary_Count',
            color_continuous_scale='RdBu',
            title=f"Distribution of {target_col}"
        )
        fig_tree.update_layout(margin=dict(t=30, l=0, r=0, b=0))
        st.plotly_chart(fig_tree, use_container_width=True)
        
        # Simple Bar Chart alternative below
        st.markdown("#### Detailed Counts")
        fig_cat_bar = px.bar(
            cat_support_data,
            x=target_col,
            y='Beneficiary_Count',
            color='Beneficiary_Count',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_cat_bar, use_container_width=True)
        
    else:
        st.warning(f"Column '{target_col}' not found in dashboard data. Please check your CSV column names.")


