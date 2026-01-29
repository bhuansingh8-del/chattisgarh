import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Green Economy Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL STYLING ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-bottom: 2rem;}
        
        /* Metric Cards */
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1.1rem;
            font-weight: 600;
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
    st.error("Data file 'dashboard_data.csv' not found. Please run the processing script first.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Control Panel")
    st.markdown("---")
    
    # District Filter
    all_districts = sorted(df['district_name'].unique())
    container = st.container()
    if st.checkbox("Select All Districts", value=True):
        selected_districts = container.multiselect("Districts", options=all_districts, default=all_districts, disabled=True)
    else:
        selected_districts = container.multiselect("Districts", options=all_districts, default=all_districts[:1])
    
    if not selected_districts:
        st.warning("Please select at least one district.")
        st.stop()
        
    st.markdown("---")
    st.caption("v5.0 | High-Definition Visuals")

df_filtered = df[df['district_name'].isin(selected_districts)]

# --- METRICS ---
st.title("Strategic Green Economy Dashboard")
st.markdown("---")

total_int = df_filtered['Beneficiary_Count'].sum()
top_lcat = df_filtered.groupby('lcat')['Beneficiary_Count'].sum().idxmax() if 'lcat' in df_filtered.columns else "N/A"
top_pillar = df_filtered.groupby('GETM')['Beneficiary_Count'].sum().idxmax() if 'GETM' in df_filtered.columns else "N/A"

c1, c2, c3 = st.columns(3)
c1.metric("Total Interventions", f"{total_int:,.0f}")
c2.metric("Dominant LCAT", top_lcat)
c3.metric("Top Green Pillar", top_pillar)

# --- TABS ---
tab1, tab2, tab3 = st.tabs([" Heatmaps (District vs GETM)", " Strategic Flow (Sankey)", " Executive Summary"])

# --- TAB 1: DISTRICT HEATMAPS (IMPROVED) ---
with tab1:
    st.subheader("Regional Intensity: District vs. Green Economy Pillar")
    st.markdown("Darker colors indicate higher volume of interventions. Values are shown inside cells.")
    
    if 'GETM' in df_filtered.columns:
        # 1. Prepare Data
        heatmap_data = df_filtered.pivot_table(
            index='district_name', 
            columns='GETM', 
            values='Beneficiary_Count', 
            aggfunc='sum',
            fill_value=0
        )
        
        # 2. Plot High-Quality Heatmap
        fig_heat = px.imshow(
            heatmap_data,
            labels=dict(x="Green Economy Pillar", y="District", color="Count"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            aspect="auto",
            color_continuous_scale="Tealgrn", # Professional Green Scale
            text_auto=True # Shows numbers inside the squares
        )
        
        fig_heat.update_layout(
            height=800, # Taller for better readability
            xaxis_title=None,
            yaxis_title=None,
            font=dict(size=12)
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.warning("GETM data missing.")

# --- TAB 2: SANKEY (HD & SHARP) ---
with tab2:
    st.subheader("Strategic Flow: LCAT ➝ Green Economy Pillar")
    
    if 'lcat' in df_filtered.columns and 'GETM' in df_filtered.columns:
        
        # 1. Aggregate Data
        sankey_data = df_filtered.groupby(['lcat', 'GETM'])['Beneficiary_Count'].sum().reset_index()
        
        # 2. Create Labels & Indices
        lcat_labels = sorted(list(sankey_data['lcat'].unique()))
        getm_labels = sorted(list(sankey_data['GETM'].unique()))
        all_labels = lcat_labels + getm_labels
        label_map = {label: i for i, label in enumerate(all_labels)}
        
        # 3. Define Sources/Targets
        sources = sankey_data['lcat'].map(label_map).tolist()
        targets = sankey_data['GETM'].map(label_map).tolist()
        values = sankey_data['Beneficiary_Count'].tolist()
        
        # 4. Custom Colors (Sharp & Professional)
        # LCAT nodes = Muted Blue, GETM nodes = Vibrant Green
        node_colors = ["#4A90E2"] * len(lcat_labels) + ["#2ECC71"] * len(getm_labels)
        
        # 5. Build Chart
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,            # More space between blocks
                thickness=30,      # Thicker blocks for better visibility
                line=dict(color="black", width=0.5),
                label=all_labels,
                color=node_colors,
                hovertemplate='%{label}<br>Total: %{value}<extra></extra>'
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color='rgba(189, 195, 199, 0.4)' # Clean, semi-transparent grey links
            )
        )])
        
        fig_sankey.update_layout(
            font_size=14,  # Bigger text for sharpness
            height=800,    # Much taller to prevent blurring
            margin=dict(t=30, b=30, l=30, r=30)
        )
        st.plotly_chart(fig_sankey, use_container_width=True)
        
    else:
        st.warning("Data missing for Sankey.")

# --- TAB 3: EXECUTIVE SUMMARY ---
with tab3:
    c1, c2 = st.columns((2,1))
    with c1:
        st.subheader("Top Support Requested")
        top_supp = df_filtered.groupby('typeofsupport')['Beneficiary_Count'].sum().nlargest(10).reset_index().sort_values('Beneficiary_Count')
        fig_bar = px.bar(top_supp, x='Beneficiary_Count', y='typeofsupport', orientation='h', text='Beneficiary_Count', color='Beneficiary_Count', color_continuous_scale='Blues')
        fig_bar.update_layout(yaxis_title=None, xaxis_title=None, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c2:
        st.subheader("Category of Support")
        if 'categoryofsupport' in df_filtered.columns:
            cat_data = df_filtered.groupby('categoryofsupport')['Beneficiary_Count'].sum().reset_index()
            fig_pie = px.pie(cat_data, values='Beneficiary_Count', names='categoryofsupport', hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_layout(showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
