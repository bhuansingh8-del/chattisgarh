import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="District Support Dashboard", layout="wide")

# Custom CSS to hide Streamlit branding and tighten layout
st.markdown("""
    <style>
        .reportview-container { margin-top: -2em; }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # Load the compressed file
    df = pd.read_csv('dashboard_data.csv')
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Data file 'dashboard_data.csv' not found. Please upload the aggregated file.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Panel")

# 1. District Slicer (Multiselect with 'All' option logic)
all_districts = sorted(df['district_name'].unique())
selected_districts = st.sidebar.multiselect(
    "Select District(s)",
    options=all_districts,
    default=all_districts[:1] # Default to first district to avoid clutter
)

if not selected_districts:
    st.warning("Please select at least one district from the sidebar.")
    st.stop()

# Filter data based on selection
df_filtered = df[df['district_name'].isin(selected_districts)]

# --- KEY METRICS ---
total_beneficiaries = df_filtered['Beneficiary_Count'].sum()
top_support = df_filtered.groupby('typeofsupport')['Beneficiary_Count'].sum().idxmax()
top_category = df_filtered.groupby('broad_category')['Beneficiary_Count'].sum().idxmax()

st.title("District Support Overview")
st.markdown("---")

# Metrics Columns
col1, col2, col3 = st.columns(3)
col1.metric("Total Interventions", f"{total_beneficiaries:,.0f}")
col2.metric("Top Support Type", top_support)
col3.metric("Leading Category", top_category)

st.markdown("---")

# --- CHARTS ROW 1 ---
c1, c2 = st.columns((2, 1))

with c1:
    st.subheader("Distribution by Broad Category")
    # Aggregating for chart
    cat_data = df_filtered.groupby('broad_category')['Beneficiary_Count'].sum().reset_index()
    
    fig_cat = px.bar(
        cat_data, 
        x='broad_category', 
        y='Beneficiary_Count',
        text='Beneficiary_Count',
        color='Beneficiary_Count',
        color_continuous_scale='Blues'
    )
    fig_cat.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig_cat.update_layout(xaxis_title=None, yaxis_title=None, showlegend=False)
    st.plotly_chart(fig_cat, use_container_width=True)

with c2:
    st.subheader("Category Share")
    fig_pie = px.donut(
        cat_data, 
        values='Beneficiary_Count', 
        names='broad_category', 
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig_pie.update_layout(showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- CHARTS ROW 2 ---
st.subheader("Top 10 Support Types")
# Top 10 breakdown
support_data = df_filtered.groupby('typeofsupport')['Beneficiary_Count'].sum().nlargest(10).reset_index()
support_data = support_data.sort_values('Beneficiary_Count', ascending=True) # Sort for horizontal bar

fig_bar = px.bar(
    support_data, 
    y='typeofsupport', 
    x='Beneficiary_Count', 
    orientation='h',
    color='Beneficiary_Count',
    color_continuous_scale='GnBu'
)
fig_bar.update_layout(xaxis_title="Count", yaxis_title=None, showlegend=False)
st.plotly_chart(fig_bar, use_container_width=True)

# --- DATA TABLE ---
with st.expander("View Detailed Aggregated Data"):
    st.dataframe(df_filtered, use_container_width=True)