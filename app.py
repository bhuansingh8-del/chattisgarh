import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Strategic Intervention Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL STYLING (CSS) ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-bottom: 2rem;}
        
        /* Metric Cards Styling */
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 10px;
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .metric-label {
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 5px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2c3e50;
        }
        .metric-sub {
            font-size: 0.75rem;
            color: #95a5a6;
            margin-top: 2px;
        }
        
        /* Tab Text Styling */
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1rem;
            font-weight: 500;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('dashboard_data.csv')
        # Ensure string types
        for col in ['lcat', 'GETM', 'district_name']:
            if col in df.columns:
                df[col] = df[col].astype(str)
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("Data file 'dashboard_data.csv' not found.")
    st.stop()

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("Filter Panel")
    st.markdown("---")
    
    # District Filter
    all_districts = sorted(df['district_name'].unique())
    container = st.container()
    if st.checkbox("Select All Districts", value=True):
        selected_districts = container.multiselect("Select Districts", options=all_districts, default=all_districts, disabled=True)
    else:
        selected_districts = container.multiselect("Select Districts", options=all_districts, default=all_districts[:1])
    
    if not selected_districts:
        st.warning("Please select at least one district.")
        st.stop()
        
    st.markdown("---")
    st.caption("Dashboard v7.0 | Professional Edition")

# --- DATA SLICING ---
# 1. State Data (Unfiltered) - For "State Overview" section
df_state = df.copy()

# 2. Filtered Data - For the rest of the dashboard
df_filtered = df[df['district_name'].isin(selected_districts)]

# --- MAIN DASHBOARD ---
st.title("Strategic Green Economy Dashboard")
st.markdown("---")

# --- TOP METRICS (FILTERED VIEW) ---
total_int = df_filtered['Beneficiary_Count'].sum()
top_lcat = df_filtered.groupby('lcat')['Beneficiary_Count'].sum().idxmax() if 'lcat' in df_filtered.columns else "N/A"
top_pillar = df_filtered.groupby('GETM')['Beneficiary_Count'].sum().idxmax() if 'GETM' in df_filtered.columns else "N/A"

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Interventions</div><div class="metric-value">{total_int:,.0f}</div><div class="metric-sub">Selected Districts</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Dominant LCAT</div><div class="metric-value">{top_lcat}</div><div class="metric-sub">Highest Volume Category</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Top Green Pillar</div><div class="metric-value">{top_pillar}</div><div class="metric-sub">Strategic Focus</div></div>""", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["Executive Summary", "Strategic Flow (Sankey)", "Heatmaps & Analysis"])

# --- TAB 1: EXECUTIVE SUMMARY ---
with tab1:
    # 1. STATE OVERVIEW SECTION
    st.subheader("State Level Snapshot (All Districts)")
    with st.expander("View Statewide Aggregates", expanded=True):
        s1, s2, s3, s4 = st.columns(4)
        state_total = df_state['Beneficiary_Count'].sum()
        state_districts = df_state['district_name'].nunique()
        state_blocks = df_state['block_name'].nunique() if 'block_name' in df_state.columns else 0
        
        s1.metric("State Total Interventions", f"{state_total:,.0f}")
        s2.metric("Total Districts Covered", state_districts)
        s3.metric("Total Active Blocks", state_blocks)
        s4.metric("Selection vs State %", f"{(total_int/state_total)*100:.1f}%")

    st.markdown("---")
    
    # 2. CATEGORY CHARTS
    c1, c2 = st.columns((2, 1))
    
    with c1:
        st.subheader("Top Support Requested")
        top_supp = df_filtered.groupby('typeofsupport')['Beneficiary_Count'].sum().nlargest(10).reset_index().sort_values('Beneficiary_Count')
        fig_bar = px.bar(
            top_supp, 
            x='Beneficiary_Count', 
            y='typeofsupport', 
            orientation='h', 
            text='Beneficiary_Count', 
            color='Beneficiary_Count', 
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(yaxis_title=None, xaxis_title=None, showlegend=False, plot_bgcolor='white')
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Category of Support")
        if 'categoryofsupport' in df_filtered.columns:
            cat_data = df_filtered.groupby('categoryofsupport')['Beneficiary_Count'].sum().reset_index()
            fig_pie = px.pie(
                cat_data, 
                values='Beneficiary_Count', 
                names='categoryofsupport', 
                hole=0.6, 
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Category of support data missing.")

# --- TAB 2: SANKEY DIAGRAM ---
with tab2:
    st.subheader("Strategic Flow: LCAT to Green Economy Pillar")
    st.markdown("Visualizing the flow of resources from functional categories to strategic pillars.")
    
    if 'lcat' in df_filtered.columns and 'GETM' in df_filtered.columns:
        sankey_data = df_filtered.groupby(['lcat', 'GETM'])['Beneficiary_Count'].sum().reset_index()
        
        lcat_labels = sorted(list(sankey_data['lcat'].unique()))
        getm_labels = sorted(list(sankey_data['GETM'].unique()))
        all_labels = lcat_labels + getm_labels
        label_map = {label: i for i, label in enumerate(all_labels)}
        
        sources = sankey_data['lcat'].map(label_map).tolist()
        targets = sankey_data['GETM'].map(label_map).tolist()
        values = sankey_data['Beneficiary_Count'].tolist()
        
        node_colors = ["#3498db"] * len(lcat_labels) + ["#27ae60"] * len(getm_labels)
        
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20, thickness=20, line=dict(color="black", width=0.5),
                label=all_labels, color=node_colors,
                hovertemplate='<b>%{label}</b><br>Volume: %{value}<extra></extra>'
            ),
            link=dict(
                source=sources, target=targets, value=values,
                color='rgba(189, 195, 199, 0.4)'
            )
        )])
        
        fig_sankey.update_layout(font=dict(size=12, color="black", family="Arial"), height=700)
        st.plotly_chart(fig_sankey, use_container_width=True)
    else:
        st.warning("Data missing for Sankey flow.")

# --- TAB 3: HEATMAPS ---
with tab3:
    st.header("Regional Density Analysis")
    
    # HEATMAP 1: DISTRICT vs GREEN ECONOMY PILLAR
    st.subheader("1. District vs. Green Economy Pillar")
    if 'GETM' in df_filtered.columns:
        hm_data1 = df_filtered.pivot_table(index='district_name', columns='GETM', values='Beneficiary_Count', aggfunc='sum', fill_value=0)
        fig_heat1 = px.imshow(
            hm_data1, 
            labels=dict(x="Pillar", y="District", color="Count"),
            x=hm_data1.columns, y=hm_data1.index, aspect="auto",
            color_continuous_scale="Tealgrn", text_auto=True
        )
        fig_heat1.update_layout(height=600)
        st.plotly_chart(fig_heat1, use_container_width=True)
    
    st.markdown("---")

    # HEATMAP 2: DISTRICT vs TOP 10 SUPPORT TYPES (NEW)
    st.subheader("2. District vs. Top 10 Support Types")
    st.markdown("Focusing on the highest volume interventions.")
    
    # Logic: Get top 10 support types first, then filter data
    top_10_types = df_filtered.groupby('typeofsupport')['Beneficiary_Count'].sum().nlargest(10).index.tolist()
    df_top_10 = df_filtered[df_filtered['typeofsupport'].isin(top_10_types)]
    
    hm_data2 = df_top_10.pivot_table(index='district_name', columns='typeofsupport', values='Beneficiary_Count', aggfunc='sum', fill_value=0)
    
    fig_heat2 = px.imshow(
        hm_data2,
        labels=dict(x="Support Type", y="District", color="Count"),
        x=hm_data2.columns, y=hm_data2.index, aspect="auto",
        color_continuous_scale="Blues", text_auto=True
    )
    fig_heat2.update_layout(height=600)
    st.plotly_chart(fig_heat2, use_container_width=True)
