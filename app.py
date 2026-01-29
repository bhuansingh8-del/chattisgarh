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
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('dashboard_data.csv')
        # Ensure string types for categorical data to avoid errors
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

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("🔍 Control Panel")
    st.markdown("---")
    
    # 1. District Filter (Global)
    all_districts = sorted(df['district_name'].unique())
    
    # "Select All" Logic
    container = st.container()
    all_selected = st.checkbox("Select All Districts", value=True)
    
    if all_selected:
        selected_districts = container.multiselect("Districts", options=all_districts, default=all_districts, disabled=True)
    else:
        selected_districts = container.multiselect("Districts", options=all_districts, default=all_districts[:1])
    
    if not selected_districts:
        st.warning("Please select at least one district.")
        st.stop()
        
    st.markdown("---")
    
    # 2. Drill Down Filter (For Sankey/Heatmaps)
    st.subheader("🎯 Focus Area")
    st.info("Use this to drill down into a specific Green Economy Pillar.")
    
    all_pillars = sorted(df['GETM'].unique()) if 'GETM' in df.columns else []
    selected_pillar = st.selectbox("Highlight Pillar:", ["All Pillars"] + all_pillars)
    
    st.caption("v4.0 | Green Economy Visualization")

# Filter Data based on District
df_filtered = df[df['district_name'].isin(selected_districts)]

# Further filter if a specific Pillar is selected (Drill Down)
if selected_pillar != "All Pillars":
    df_filtered = df_filtered[df_filtered['GETM'] == selected_pillar]

# --- MAIN DASHBOARD ---
st.title("🌿 Strategic Green Economy Dashboard")
st.markdown("### Feasibility & Strategic Alignment Analysis")
st.markdown("---")

# Metrics
total_int = df_filtered['Beneficiary_Count'].sum()
top_lcat = df_filtered.groupby('lcat')['Beneficiary_Count'].sum().idxmax() if 'lcat' in df_filtered.columns else "N/A"
top_pillar = df_filtered.groupby('GETM')['Beneficiary_Count'].sum().idxmax() if 'GETM' in df_filtered.columns else "N/A"

c1, c2, c3 = st.columns(3)
c1.metric("Total Interventions", f"{total_int:,.0f}")
c2.metric("Dominant LCAT", top_lcat)
c3.metric("Top Green Pillar", top_pillar)

st.markdown("<br>", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🌱 Green Economy (Strategic Flow)", "📊 Executive Summary", "📍 District Heatmaps"])

# --- TAB 1: SANKEY & STRATEGIC FLOW ---
with tab1:
    st.subheader("Strategic Flow: LCAT ➝ Green Economy Pillar")
    st.markdown("Visualizing how input categories map to strategic green goals.")
    
    if 'lcat' in df_filtered.columns and 'GETM' in df_filtered.columns:
        
        # --- SANKEY DIAGRAM PREPARATION ---
        # 1. Aggregate data for flow
        sankey_data = df_filtered.groupby(['lcat', 'GETM'])['Beneficiary_Count'].sum().reset_index()
        
        # 2. Create unique labels
        # We need a list of all unique nodes (Source Labels + Target Labels)
        lcat_labels = list(sankey_data['lcat'].unique())
        getm_labels = list(sankey_data['GETM'].unique())
        all_labels = lcat_labels + getm_labels
        
        # 3. Map labels to indices (0, 1, 2...)
        label_map = {label: i for i, label in enumerate(all_labels)}
        
        # 4. Create Source, Target, Value lists
        sources = sankey_data['lcat'].map(label_map).tolist()
        targets = sankey_data['GETM'].map(label_map).tolist()
        values = sankey_data['Beneficiary_Count'].tolist()
        
        # 5. Define Colors (Professional Palette)
        # Give LCATs one color set, Pillars another
        node_colors = ["#636EFA"] * len(lcat_labels) + ["#00CC96"] * len(getm_labels)
        
        # 6. Plot
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_labels,
                color=node_colors
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color='rgba(100, 100, 100, 0.2)' # Semi-transparent grey for links
            )
        )])
        
        fig_sankey.update_layout(title_text="Flow Volume: LCAT to Green Economy Pillar", font_size=12, height=600)
        st.plotly_chart(fig_sankey, use_container_width=True)
        
        st.markdown("---")
        
        # --- BUBBLE CHART ---
        st.subheader("Cluster Analysis: LCAT vs. Green Economy Pillar")
        
        bubble_data = df_filtered.groupby(['lcat', 'GETM'])['Beneficiary_Count'].sum().reset_index()
        
        fig_bubble = px.scatter(
            bubble_data,
            x="lcat",
            y="GETM",
            size="Beneficiary_Count",
            color="GETM",
            hover_name="lcat",
            size_max=60,
            title="Feasibility Bubble Map (Size = Volume)",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_bubble.update_layout(xaxis_title="LCAT Category", yaxis_title="Green Economy Pillar", showlegend=False, height=500)
        st.plotly_chart(fig_bubble, use_container_width=True)
        
    else:
        st.warning("Data for Sankey (lcat/GETM) is missing.")

# --- TAB 2: EXECUTIVE SUMMARY ---
with tab2:
    col_left, col_right = st.columns((2, 1))
    
    with col_left:
        st.subheader("Top Support Requested")
        top_support = df_filtered.groupby('typeofsupport')['Beneficiary_Count'].sum().nlargest(10).reset_index().sort_values('Beneficiary_Count')
        fig_bar = px.bar(top_support, x='Beneficiary_Count', y='typeofsupport', orientation='h', text='Beneficiary_Count', color='Beneficiary_Count', color_continuous_scale='Blues')
        fig_bar.update_layout(yaxis_title=None, xaxis_title="Interventions")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        # THE REQUESTED SINGLE CHART FOR CATEGORY OF SUPPORT
        st.subheader("Category of Support")
        if 'categoryofsupport' in df_filtered.columns:
            cat_data = df_filtered.groupby('categoryofsupport')['Beneficiary_Count'].sum().reset_index()
            fig_pie = px.pie(cat_data, values='Beneficiary_Count', names='categoryofsupport', hole=0.6, color_discrete_sequence=px.colors.sequential.RdBu)
            fig_pie.update_layout(showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Category of support data missing.")

# --- TAB 3: DISTRICT HEATMAPS ---
with tab3:
    st.subheader("Regional Intensity: Where is the Green Economy Growing?")
    
    if 'GETM' in df_filtered.columns:
        # Matrix: District vs Green Economy Pillar
        heatmap_data = df_filtered.pivot_table(
            index='district_name', 
            columns='GETM', 
            values='Beneficiary_Count', 
            aggfunc='sum',
            fill_value=0
        )
        
        fig_heat = px.imshow(
            heatmap_data,
            labels=dict(x="Green Economy Pillar", y="District", color="Interventions"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            aspect="auto",
            color_continuous_scale="Viridis",
            title="Heatmap: District vs. Green Economy Pillar"
        )
        fig_heat.update_layout(height=600)
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.warning("GETM data missing for heatmap.")
