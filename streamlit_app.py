"""
Soccer Analytics Dashboard - Streamlit Version

A Streamlit-based web application that provides an interactive dashboard for soccer analytics,
allowing users to explore player data, compare performances, and generate insights
using the PSCDL framework.

Author: Michael Xu
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import warnings
warnings.filterwarnings('ignore')

# Import our analytics modules
import importlib.util
import sys
from pathlib import Path

def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load analytics modules
try:
    recruitment_analyzer = load_module("recruitment_analyzer", "04_recruitment_analyzer.py")
    RecruitmentAnalyzer = recruitment_analyzer.RecruitmentAnalyzer
except Exception as e:
    st.warning(f"Could not load recruitment analyzer: {e}")
    RecruitmentAnalyzer = None

# Page configuration
st.set_page_config(
    page_title="Soccer Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set theme to light mode
st.markdown("""
<script>
    // Force light theme
    if (window.parent !== window) {
        window.parent.postMessage({
            type: 'streamlit:setThemeConfig',
            themeConfig: {
                base: 'light',
                primaryColor: '#2E8B57',
                backgroundColor: '#FFFFFF',
                secondaryBackgroundColor: '#F0F8F0',
                textColor: '#262730'
            }
        }, '*');
    }
</script>
""", unsafe_allow_html=True)

# Custom CSS for green theme with white background
st.markdown("""
<style>
    /* Set overall page background to white */
    .main .block-container {
        background-color: white;
    }
    
    .stApp {
        background-color: white;
    }
    
    .main-header {
        background: linear-gradient(135deg, #2E8B57, #32CD32, #90EE90);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #2E8B57, #32CD32);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .section-header {
        background: linear-gradient(135deg, #2E8B57, #32CD32);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    
    .stSelectbox > div > div {
        background-color: #f0f8f0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2E8B57, #32CD32);
        color: white;
        border: none;
        border-radius: 5px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #228B22, #00FF00);
        color: white;
    }
    
    /* Ensure all text is dark on white background */
    .main .block-container p, 
    .main .block-container h1, 
    .main .block-container h2, 
    .main .block-container h3, 
    .main .block-container h4, 
    .main .block-container h5, 
    .main .block-container h6 {
        color: #262730;
    }
    
    /* Style the sidebar if needed */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load the soccer analytics data with caching"""
    try:
        stats_dir = Path("Statistics")
        performance_file = stats_dir / "statistics_performance_scores.csv"
        totals_file = stats_dir / "statistics_totals.csv"
        
        if not performance_file.exists() or not totals_file.exists():
            return None, None, None, "Statistics files not found. Please run the pipeline first."
        
        performance_df = pd.read_csv(performance_file)
        totals_df = pd.read_csv(totals_file)
        
        if RecruitmentAnalyzer:
            analyzer = RecruitmentAnalyzer(performance_df, totals_df)
            recruitment_df = analyzer.recruitment_df
            # Add radar area metrics for scatter plot
            analyzer.add_radar_area_metric(verbose=False)
            recruitment_df = analyzer.recruitment_df
        else:
            # Create basic recruitment dataframe
            recruitment_df = performance_df.merge(
                totals_df[['player_id', 'player_name', 'total_games', 'total_minutes_played']], 
                on=['player_id', 'player_name'], 
                how='left'
            )
            # Calculate radar area metrics manually for basic case
            recruitment_df = add_radar_area_metric(recruitment_df)
        
        return performance_df, totals_df, recruitment_df, "Data loaded successfully"
        
    except Exception as e:
        return None, None, None, f"Error loading data: {e}"

def add_radar_area_metric(df):
    """Add radar area metrics to recruitment_df for basic case"""
    def calculate_radar_area(scores):
        """Calculate the area of a radar chart polygon"""
        if len(scores) < 3:
            return 0
        
        # Convert to radians and calculate area using shoelace formula
        angles = np.linspace(0, 2 * np.pi, len(scores), endpoint=False)
        x = scores * np.cos(angles)
        y = scores * np.sin(angles)
        
        # Shoelace formula
        area = 0.5 * abs(sum(x[i] * y[(i + 1) % len(y)] - x[(i + 1) % len(x)] * y[i] 
                           for i in range(len(x))))
        return area
    
    # Calculate radar areas for each player
    radar_areas = []
    for _, player in df.iterrows():
        scores = [player['P_score'], player['S_score'], player['C_score'], 
                 player['D_score'], player['L_score']]
        area = calculate_radar_area(scores)
        radar_areas.append(area)
    
    df['radar_area'] = radar_areas
    
    # Normalize to 0-100 scale (theoretical max area for 100x100 square)
    theoretical_max_area = 0.5 * 100 * 100 * np.sin(2 * np.pi / 5)  # Regular pentagon
    df['radar_area_normalized'] = (df['radar_area'] / theoretical_max_area) * 100
    
    return df

def create_performance_distribution_chart(recruitment_df):
    """Create performance score distribution chart"""
    scores = recruitment_df['performance_score'].dropna()
    
    # Calculate histogram
    hist, bin_edges = np.histogram(scores, bins=30)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Calculate statistics
    mean_score = scores.mean()
    top_10_threshold = scores.quantile(0.9)
    
    fig = go.Figure()
    
    # Add histogram bars
    fig.add_trace(go.Bar(
        x=bin_centers,
        y=hist,
        name='Performance Score Distribution',
        marker_color='#636efa',
        hovertemplate='<b>Score:</b> %{x}<br><b>Count:</b> %{y}<extra></extra>'
    ))
    
    # Add vertical lines with annotations at the top
    fig.add_vline(x=mean_score, line_dash="dash", line_color="red", 
                  annotation_text=f"<b style='color: black;'>Mean: {mean_score:.1f}</b>",
                  annotation_position="top")
    fig.add_vline(x=top_10_threshold, line_dash="dash", line_color="orange", 
                  annotation_text=f"<b style='color: black;'>Top 10%: {top_10_threshold:.1f}</b>",
                  annotation_position="top")
    
    fig.update_layout(
        title='Performance Score Distribution',
        xaxis_title='Performance Score',
        yaxis_title='Number of Players',
        height=500,
        showlegend=False
    )
    
    return fig

def create_top_specialists_chart(recruitment_df, category='performance_score', limit=10):
    """Create top performers bar chart"""
    qualified_players = recruitment_df[recruitment_df['total_games'] >= 5]
    top_players = qualified_players.nlargest(limit, category)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top_players[category],
        y=top_players['player_name'],
        orientation='h',
        name=f'Top {limit} Players',
        marker_color='#636efa',
        text=[f"{val:.1f}" for val in top_players[category]],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br><b>Score:</b> %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Top {limit} Players by {category.replace("_", " ").title()}',
        xaxis_title=category.replace('_', ' ').title(),
        yaxis_title='Players',
        xaxis=dict(range=[0, 100]),
        yaxis=dict(categoryorder='total ascending'),
        height=400,
        margin=dict(l=150, r=30, t=30, b=30)
    )
    
    return fig

def create_pscdl_radar_chart(recruitment_df, player_names):
    """Create PSCDL radar chart for selected players"""
    selected_players = recruitment_df[recruitment_df['player_name'].isin(player_names)]
    
    if selected_players.empty:
        return go.Figure()
    
    categories = ['P_score', 'S_score', 'C_score', 'D_score', 'L_score']
    category_labels = ['Passing/Creation', 'Finishing/Shot', 'Carrying/1v1', 'Defending/Disruption', 'Discipline']
    
    fig = go.Figure()
    
    # Use consistent colors
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    for i, (_, player) in enumerate(selected_players.iterrows()):
        values = [player[cat] for cat in categories]
        values += values[:1]  # Complete the circle
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=category_labels + [category_labels[0]],  # Complete the circle
            fill='toself',
            name=player['player_name'],
            line_color=colors[i % len(colors)],
            fillcolor=colors[i % len(colors)],
            opacity=0.5
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="PSCDL Performance Comparison",
        height=500
    )
    
    return fig

def create_pscdl_bar_chart(recruitment_df, player_names):
    """Create PSCDL bar chart for selected players"""
    selected_players = recruitment_df[recruitment_df['player_name'].isin(player_names)]
    
    if selected_players.empty:
        return go.Figure()
    
    categories = ['P_score', 'S_score', 'C_score', 'D_score', 'L_score']
    category_labels = ['Passing/Creation', 'Finishing/Shot', 'Carrying/1v1', 'Defending/Disruption', 'Discipline']
    
    # Use consistent colors
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    fig = go.Figure()
    
    for i, (_, player) in enumerate(selected_players.iterrows()):
        scores = [player[cat] for cat in categories]
        
        fig.add_trace(go.Bar(
            x=category_labels,
            y=scores,
            name=player['player_name'],
            marker_color=colors[i % len(colors)],
            text=[f"{score:.1f}" for score in scores],
            textposition='outside',
            hovertemplate='<b>%{fullData.name}</b><br><b>Area:</b> %{x}<br><b>Score:</b> %{y}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Specialist Score Comparison',
        xaxis_title='Specialist Areas',
        yaxis_title='Score',
        yaxis=dict(range=[0, 100]),
        barmode='group',
        height=500,
        margin=dict(l=100, r=50, t=50, b=50)
    )
    
    return fig

def create_scatter_plot(recruitment_df, x_col='performance_score', y_col='radar_area_normalized'):
    """Create scatter plot for custom x and y axes"""
    available_metrics = {
        'performance_score': 'PSCDL Performance Score',
        'P_score': 'Passing/Creation Score',
        'S_score': 'Finishing/Shot Value Score', 
        'C_score': 'Carrying/1v1 Score',
        'D_score': 'Defending/Disruption Score',
        'L_score': 'Discipline Score',
        'radar_area_normalized': 'Ability Coverage (Radar Area)',
        'total_games': 'Total Games Played',
        'total_minutes_played': 'Total Minutes Played'
    }
    
    # Validate columns exist
    if x_col not in recruitment_df.columns or y_col not in recruitment_df.columns:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=recruitment_df[x_col],
        y=recruitment_df[y_col],
        mode='markers',
        name='Players',
        marker=dict(color='#636efa', size=8, opacity=0.7),
        text=recruitment_df['player_name'],
        hovertemplate=f'<b>%{{text}}</b><br>{available_metrics.get(x_col, x_col.replace("_", " ").title())}: %{{x}}<br>{available_metrics.get(y_col, y_col.replace("_", " ").title())}: %{{y}}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'{available_metrics.get(x_col, x_col.replace("_", " ").title())} vs {available_metrics.get(y_col, y_col.replace("_", " ").title())}',
        xaxis_title=available_metrics.get(x_col, x_col.replace('_', ' ').title()),
        yaxis_title=available_metrics.get(y_col, y_col.replace('_', ' ').title()),
        height=500,
        margin=dict(l=100, r=50, t=50, b=50)
    )
    
    return fig

def create_basic_stats_chart(totals_df, stat_type='goals', limit=10):
    """Create basic statistics chart showing top performers in key stats"""
    all_stats = {
        'total_goals': {'name': 'Goals', 'color': '#FF6B6B'},
        'total_xg': {'name': 'Expected Goals (xG)', 'color': '#4ECDC4'},
        'total_assists': {'name': 'Assists', 'color': '#45B7D1'},
        'total_interceptions': {'name': 'Interceptions', 'color': '#96CEB4'},
        'total_tackles': {'name': 'Tackles', 'color': '#c80ee1'},
        'total_fouls_committed': {'name': 'Fouls Committed', 'color': '#FFEAA7'}
    }
    
    stat_mapping = {
        'goals': 'total_goals',
        'xg': 'total_xg',
        'assists': 'total_assists',
        'interceptions': 'total_interceptions',
        'tackles': 'total_tackles',
        'fouls': 'total_fouls_committed'
    }
    
    if stat_type not in stat_mapping:
        return go.Figure()
    
    stat_col = stat_mapping[stat_type]
    stat_info = all_stats[stat_col]
    
    if stat_col not in totals_df.columns:
        return go.Figure()
    
    # Get top players for this stat
    top_players = totals_df.nlargest(limit, stat_col)
    top_players = top_players[top_players[stat_col].notna() & (top_players[stat_col] > 0)]
    
    if len(top_players) == 0:
        return go.Figure()
    
    # Reverse the order to show highest values at the top
    top_players = top_players.iloc[::-1]
    
    # Format text labels based on stat type
    if stat_type == 'xg':
        text_labels = [f"{val:.2f}" for val in top_players[stat_col].tolist()]
    else:
        text_labels = [f"{int(val)}" for val in top_players[stat_col].tolist()]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top_players[stat_col],
        y=top_players['player_name'],
        orientation='h',
        name=stat_info['name'],
        marker_color=stat_info['color'],
        text=text_labels,
        textposition='outside',
        hovertemplate='<b>%{y}</b><br><b>Count:</b> %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Statistics Leaders - {stat_info["name"]}',
        xaxis_title='Count',
        height=600,
        margin=dict(l=200, r=100, t=50, b=50)
    )
    
    return fig

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1><i class="fas fa-futbol"></i> Soccer Analytics Dashboard</h1>
        <p style="margin: 0; font-size: 1.2em;">Designed by Michael Xu</p>
    </div>
    """, unsafe_allow_html=True)
    
    # PSCDL Framework Introduction
    st.markdown("""
    <div class="section-header">
        <h3><i class="fas fa-chart-line"></i> ⚽️ PSCDL Scoring Framework</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **PSCDL scoring score** is a 5-subscore performance framework that evaluates players across five critical dimensions: 
    **Passing/Creation (P)**, **Finishing/Shot Value (S)**, **Carrying/1v1 (C)**, **Defending/Disruption (D)**, and **Discipline (L)**. 
    These metrics are highly relevant for scouting because they capture the essential skills needed in modern soccer. 
    The framework includes 40+ statistical measures such as pass accuracy, progressive passes, xG per shot, successful dribbles, 
    tackle success rates, and interceptions per 90 minutes. **This standardized approach allows scouts to identify both specialists 
    (elite performers in specific areas) and all-rounders (balanced across multiple facets), enabling targeted recruitment based on tactical needs**.
    """)
    
    # Load data
    performance_df, totals_df, recruitment_df, message = load_data()
    
    if recruitment_df is None:
        st.error(message)
        return
    
    # Display success message
    st.success(message)
    
    # Calculate KPIs
    total_players = len(recruitment_df)
    mean_performance = recruitment_df['performance_score'].mean()
    top_10_threshold = recruitment_df['performance_score'].quantile(0.9)
    top_10_players = len(recruitment_df[recruitment_df['performance_score'] >= top_10_threshold])
    
    # Display KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{total_players}</h2>
            <p>Total Players</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{mean_performance:.1f}</h2>
            <p>Mean Performance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{top_10_threshold:.1f}</h2>
            <p>Top 10% Threshold</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{top_10_players}</h2>
            <p>Top 10% Players</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Descriptive Analysis Section
    st.markdown("""
    <div class="section-header">
        <h3><i class="fas fa-chart-bar"></i> 📈 Descriptive Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Distribution Chart

    st.plotly_chart(create_performance_distribution_chart(recruitment_df), width='stretch', key="distribution_chart")
       
    # Basic Statistics Selector

    st.markdown("""
    <div class="section-header">
        <h3><i class="fas fa-chart-bar"></i> 📊 Basic Statistics Leaders</h3>
    </div>
    """, unsafe_allow_html=True)
    
    stat_type = st.selectbox(
        "Select Statistics:",
        ['goals', 'xg', 'assists', 'interceptions', 'tackles', 'fouls'],
        format_func=lambda x: {
            'goals': 'Goals',
            'xg': 'Expected Goals (xG)',
            'assists': 'Assists',
            'interceptions': 'Interceptions',
            'tackles': 'Tackles',
            'fouls': 'Fouls Committed'
        }[x],
        key="basic_stats_selector"
    )
    
    st.plotly_chart(create_basic_stats_chart(totals_df, stat_type, 10), width='stretch', key=f"basic_stats_{stat_type}")
    
    # Top Performers & Specialists Section
    st.markdown("""
    <div class="section-header">
        <h3><i class="fas fa-trophy"></i> 🏆 Top Performers & Specialists</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1.5])
    
    with col1:
        # Category selector
        category = st.selectbox(
            "Select Category:",
            ['performance_score', 'P_score', 'S_score', 'C_score', 'D_score'],
            format_func=lambda x: {
                'performance_score': 'PSCDL Performance Score',
                'P_score': 'Passing/Creation',
                'S_score': 'Finishing/Shot',
                'C_score': 'Carrying/1v1',
                'D_score': 'Defending/Disruption'
            }[x],
            key="top_specialists_selector"
        )
        
        st.plotly_chart(create_top_specialists_chart(recruitment_df, category, 10), width='stretch', key=f"top_specialists_{category}")
    
    with col2:
        # Top specialists table
        qualified_players = recruitment_df[recruitment_df['total_games'] >= 5]
        top_specialists = qualified_players.nlargest(10, category)
        
        st.subheader("Top Specialists Table")
        display_df = top_specialists[['player_name', 'team', category, 'total_games']].copy()
        display_df.columns = ['Player', 'Team', category.replace('_', ' ').title(), 'Games']
        st.dataframe(display_df, use_container_width=True, height=400)
    
    # Postscript
    st.info("**P.S: Only players with at least 5 games played are included.**")
    
    # Player Comparison Dashboard
    st.markdown("""
    <div class="section-header">
        <h3><i class="fas fa-users"></i> 👥 Player Comparison Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Player selection
    all_players = recruitment_df['player_name'].tolist()
    selected_players = st.multiselect(
        "Select Players (max 6):",
        all_players,
        default=["Vivianne Miedema", "Caroline Weir"],
        max_selections=6,
        key="player_selector"
    )
    
    if selected_players:
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_pscdl_bar_chart(recruitment_df, selected_players), width='stretch', key="pscdl_bar_chart")
        
        with col2:
            st.plotly_chart(create_pscdl_radar_chart(recruitment_df, selected_players), width='stretch', key="pscdl_radar_chart")
    
    # Custom Scatter Plot Analysis
    st.markdown("""
    <div class="section-header">
        <h3><i class="fas fa-chart-scatter"></i> 📍 Custom Scatter Plot Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        x_axis = st.selectbox(
            "X-Axis (Horizontal):",
            ['performance_score', 'P_score', 'S_score', 'C_score', 'D_score', 'L_score', 'radar_area_normalized', 'total_games', 'total_minutes_played'],
            format_func=lambda x: {
                'performance_score': 'PSCDL Performance Score',
                'P_score': 'Passing/Creation Score',
                'S_score': 'Finishing/Shot Value Score',
                'C_score': 'Carrying/1v1 Score',
                'D_score': 'Defending/Disruption Score',
                'L_score': 'Discipline Score',
                'radar_area_normalized': 'Ability Coverage (Radar Area)',
                'total_games': 'Total Games Played',
                'total_minutes_played': 'Total Minutes Played'
            }[x],
            key="x_axis_selector"
        )
    
    with col2:
        y_axis = st.selectbox(
            "Y-Axis (Vertical):",
            ['radar_area_normalized', 'performance_score', 'P_score', 'S_score', 'C_score', 'D_score', 'L_score', 'total_games', 'total_minutes_played'],
            format_func=lambda x: {
                'performance_score': 'PSCDL Performance Score',
                'P_score': 'Passing/Creation Score',
                'S_score': 'Finishing/Shot Value Score',
                'C_score': 'Carrying/1v1 Score',
                'D_score': 'Defending/Disruption Score',
                'L_score': 'Discipline Score',
                'radar_area_normalized': 'Ability Coverage (Radar Area)',
                'total_games': 'Total Games Played',
                'total_minutes_played': 'Total Minutes Played'
            }[x],
            key="y_axis_selector"
        )
    
    st.plotly_chart(create_scatter_plot(recruitment_df, x_axis, y_axis), width='stretch', key=f"scatter_plot_{x_axis}_{y_axis}")
    
    # Analysis Tips
    st.info("""
    **Analysis Tips:**
    - **Positive Correlation:** Points trending upward indicate players who excel in both metrics
    - **Negative Correlation:** Points trending downward suggest trade-offs between skills
    - **Clusters:** Groups of players with similar performance profiles
    - **Outliers:** Players with unique skill combinations worth investigating
    """)

if __name__ == "__main__":
    main()
