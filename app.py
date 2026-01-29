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

# --- PROFESSIONAL STYLING (Custom CSS) ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-bottom: 2rem;}
        
        /* --- CUSTOM COMPACT METRIC CARDS --- */
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            margin-bottom: 10px;
            height: 140px; /* Fixed height to keep them aligned */
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 5px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .metric-value {
            font-size: 1.4rem; /* Smaller font to fit long text */
            font-weight: 700;
            color: #333;
            line-height: 1.2;
            word-wrap: break-word; /* Force text to wrap */
        }
        
        /* Tab Text Styling */
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1rem;
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
    st.error("Data file 'dashboard_data.csv' not found.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header(" Filter Panel")
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
    st.caption("v6.0 | Sharp Visuals & Auto-Fit Text")

df_filtered = df[df['district_name'].isin(selected_districts)]

# --- METRICS (CUSTOM HTML) ---
st.title("Chattisgarh Dashboard")
st.markdown("---")

# Calculate Metrics
total_int = df_filtered['Beneficiary_Count'].sum()
top_lcat = df_filtered.groupby('lcat')['Beneficiary_Count'].sum().idxmax() if 'lcat' in df_filtered.columns else "N/A"
top_pillar = df_filtered.groupby('GETM')['Beneficiary_Count'].sum().idxmax() if 'GETM' in df_filtered.columns else "N/A"

# Render Custom Cards (These wrap text and fit better)
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Interventions</div>
            <div class="metric-value">{total_int:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Dominant LCAT</div>
            <div class="metric-value">{top_lcat}</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Top Green Pillar</div>
            <div class="metric-value">{top_pillar}</div>
        </div>
    """, unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs([" Heatmaps", " Strategic Flow (Sankey)", " Executive Summary"])

# --- TAB 1: HEATMAPS ---
with tab1:
    st.subheader("Regional Intensity: District vs. Green Economy Pillar")
    
    if 'GETM' in df_filtered.columns:
        heatmap_data = df_filtered.pivot_table(
            index='district_name', columns='GETM', values='Beneficiary_Count', aggfunc='sum', fill_value=0
        )
        
        fig_heat = px.imshow(
            heatmap_data,
            labels=dict(x="Pillar", y="District", color="Count"),
            x=heatmap_data.columns, y=heatmap_data.index,
            aspect="auto", color_continuous_scale="Tealgrn", text_auto=True
        )
        fig_heat.update_layout(height=800, font=dict(size=12))
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.warning("GETM data missing.")

# --- TAB 2: SANKEY (FIXED BLUR & SIZE) ---
with tab2:
    st.subheader("Strategic Flow: LCAT ➝ Green Economy Pillar")
    
    if 'lcat' in df_filtered.columns and 'GETM' in df_filtered.columns:
        
        # Data Prep
        sankey_data = df_filtered.groupby(['lcat', 'GETM'])['Beneficiary_Count'].sum().reset_index()
        
        lcat_labels = sorted(list(sankey_data['lcat'].unique()))
        getm_labels = sorted(list(sankey_data['GETM'].unique()))
        all_labels = lcat_labels + getm_labels
        label_map = {label: i for i, label in enumerate(all_labels)}
        
        sources = sankey_data['lcat'].map(label_map).tolist()
        targets = sankey_data['GETM'].map(label_map).tolist()
        values = sankey_data['Beneficiary_Count'].tolist()
        
        # Colors
        node_colors = ["#4A90E2"] * len(lcat_labels) + ["#2ECC71"] * len(getm_labels)
        
        # Plot
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=25,
                thickness=15,  # Reduced thickness (Solved "Boxes too big")
                line=dict(color="black", width=0.5),
                label=all_labels,
                color=node_colors,
                hovertemplate='<b>%{label}</b><br>Volume: %{value}<extra></extra>'
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color='rgba(189, 195, 199, 0.4)'
            )
        )])
        
        fig_sankey.update_layout(
            font=dict(size=13, color="black", family="Arial"), # Sharper font (Solved "Blurry")
            height=900,  # Taller height improves resolution
            margin=dict(t=40, b=40, l=40, r=40)
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

