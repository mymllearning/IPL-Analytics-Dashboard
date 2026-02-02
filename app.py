import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple, Optional
import numpy as np

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="IPL Analytics Dashboard",
    layout="wide",
    page_icon="🏏",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================

st.markdown("""
<style>
    /* Main App Styling */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        color: #e5e7eb;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #475569;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #ff4b4b 0%, #ff6b6b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 8px;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ff4b4b;
        font-weight: 700;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        color: #94a3b8;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b;
        color: white;
    }
    
    /* Divider */
    hr {
        border-color: #334155;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING AND PROCESSING
# ============================================================================

@st.cache_data(ttl=3600, show_spinner="Loading IPL data...")
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and preprocess matches and deliveries data.
    
    Returns:
        Tuple of (matches, deliveries) DataFrames
    """
    try:
        matches = pd.read_csv("data/matches.csv")
        deliveries = pd.read_csv("data/deliveries.csv")
        
        # Team name normalization
        team_mapping = {
            'Rising Pune Supergiant': 'Rising Pune Supergiants',
            'Delhi Daredevils': 'Delhi Capitals',
        }
        
        # Apply team mapping to matches
        for col in ['team1', 'team2', 'winner', 'toss_winner']:
            if col in matches.columns:
                matches[col] = matches[col].replace(team_mapping)
        
        # Apply team mapping to deliveries
        for col in ['batting_team', 'bowling_team']:
            if col in deliveries.columns:
                deliveries[col] = deliveries[col].replace(team_mapping)
        
        # Convert date to datetime
        if 'date' in matches.columns:
            matches['date'] = pd.to_datetime(matches['date'], errors='coerce')
        
        # Sort by date
        matches = matches.sort_values('date', ascending=False)
        
        return matches, deliveries
        
    except FileNotFoundError as e:
        st.error(f"❌ Data files not found: {e}")
        st.info("Please ensure 'data/matches.csv' and 'data/deliveries.csv' exist in your directory.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.stop()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_metric_card(value: any, label: str) -> str:
    """Generate HTML for a metric card."""
    formatted_value = f"{value:,}" if isinstance(value, (int, float)) else value
    return f'''
        <div class="metric-card">
            <div class="metric-value">{formatted_value}</div>
            <div class="metric-label">{label}</div>
        </div>
    '''

def get_valid_dismissals() -> list:
    """Return list of valid dismissal types that count toward bowler."""
    return ['caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket']

def calculate_strike_rate(runs: int, balls: int) -> float:
    """Calculate strike rate."""
    return (runs / balls * 100) if balls > 0 else 0

def calculate_economy(runs: int, balls: int) -> float:
    """Calculate economy rate."""
    overs = balls / 6
    return (runs / overs) if overs > 0 else 0

# ============================================================================
# LOAD DATA
# ============================================================================

matches, deliveries = load_data()

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

st.sidebar.title("🏏 IPL Analytics")
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/en/8/84/Indian_Premier_League_Official_Logo.svg",
    width=120
)

st.sidebar.markdown("---")

# Season Filter
seasons = sorted(matches['season'].unique(), reverse=True)
selected_season = st.sidebar.multiselect(
    "🗓️ Select Season(s)",
    seasons,
    default=seasons[:5] if len(seasons) >= 5 else seasons,
    help="Filter data by IPL season"
)

# Team Filter
teams = sorted(matches['team1'].dropna().unique())
selected_teams = st.sidebar.multiselect(
    "🏏 Select Team(s)",
    teams,
    default=teams,
    help="Filter matches involving specific teams"
)

# Venue Filter
venues = sorted(matches['venue'].dropna().unique())
selected_venues = st.sidebar.multiselect(
    "📍 Select Venue(s)",
    venues,
    help="Filter matches by venue (optional)"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use filters to narrow down your analysis")

# ============================================================================
# APPLY FILTERS
# ============================================================================

filtered_matches = matches.copy()

if selected_season:
    filtered_matches = filtered_matches[filtered_matches['season'].isin(selected_season)]

if selected_teams:
    filtered_matches = filtered_matches[
        (filtered_matches['team1'].isin(selected_teams)) | 
        (filtered_matches['team2'].isin(selected_teams))
    ]

if selected_venues:
    filtered_matches = filtered_matches[filtered_matches['venue'].isin(selected_venues)]

# Filter deliveries based on matches
filtered_match_ids = filtered_matches['id'].unique()
filtered_deliveries = deliveries[deliveries['match_id'].isin(filtered_match_ids)]

# ============================================================================
# HEADER
# ============================================================================

st.title("🏆 IPL Analytics Dashboard")
st.markdown(f"**Comprehensive analysis of Indian Premier League matches** ({matches['season'].min()}-{matches['season'].max()})")

# Show active filters
if selected_season or selected_teams or selected_venues:
    filter_text = []
    if selected_season:
        filter_text.append(f"Seasons: {', '.join(map(str, sorted(selected_season)))}")
    if len(selected_teams) < len(teams):
        filter_text.append(f"Teams: {len(selected_teams)} selected")
    if selected_venues:
        filter_text.append(f"Venues: {len(selected_venues)} selected")
    
    st.caption("🔍 **Active Filters:** " + " | ".join(filter_text))

st.divider()

# ============================================================================
# KEY METRICS
# ============================================================================

col1, col2, col3, col4, col5 = st.columns(5)

total_matches = filtered_matches.shape[0]
total_runs = int(filtered_deliveries['total_runs'].sum())
total_wickets = int(filtered_deliveries['player_dismissed'].notna().sum())
total_sixes = int(filtered_deliveries[filtered_deliveries['batsman_runs'] == 6].shape[0])
total_fours = int(filtered_deliveries[filtered_deliveries['batsman_runs'] == 4].shape[0])

with col1:
    st.markdown(create_metric_card(total_matches, "Total Matches"), unsafe_allow_html=True)

with col2:
    st.markdown(create_metric_card(total_runs, "Total Runs"), unsafe_allow_html=True)

with col3:
    st.markdown(create_metric_card(total_wickets, "Total Wickets"), unsafe_allow_html=True)

with col4:
    st.markdown(create_metric_card(total_sixes, "Sixes Hit"), unsafe_allow_html=True)

with col5:
    st.markdown(create_metric_card(total_fours, "Fours Hit"), unsafe_allow_html=True)

st.divider()

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏆 Match Analysis",
    "👤 Player Analysis",
    "📍 Venue Analysis",
    "⏱️ Over Analysis",
    "📊 Team Comparison",
    "🎯 Advanced Stats"
])

# ============================================================================
# TAB 1: MATCH ANALYSIS
# ============================================================================

with tab1:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📈 Matches Per Season")
        matches_per_season = filtered_matches['season'].value_counts().sort_index().reset_index()
        matches_per_season.columns = ['Season', 'Matches']
        
        fig_matches = px.bar(
            matches_per_season,
            x='Season',
            y='Matches',
            color='Matches',
            template='plotly_dark',
            color_continuous_scale='Reds',
            labels={'Matches': 'Number of Matches'},
        )
        fig_matches.update_layout(
            showlegend=False,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_matches, use_container_width=True)
    
    with col_b:
        st.subheader("🏅 Total Wins by Team")
        wins_by_team = filtered_matches['winner'].value_counts().reset_index()
        wins_by_team.columns = ['Team', 'Wins']
        wins_by_team = wins_by_team.head(10)
        
        fig_wins = px.bar(
            wins_by_team,
            x='Wins',
            y='Team',
            orientation='h',
            template='plotly_dark',
            color='Wins',
            color_continuous_scale='Viridis',
            labels={'Wins': 'Number of Wins'},
        )
        fig_wins.update_layout(
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_wins, use_container_width=True)

    st.divider()
    
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.subheader("🎲 Toss Decision Distribution")
        toss_counts = filtered_matches['toss_decision'].value_counts().reset_index()
        toss_counts.columns = ['Decision', 'Count']
        
        fig_toss = px.pie(
            toss_counts,
            names='Decision',
            values='Count',
            hole=0.4,
            template='plotly_dark',
            color_discrete_sequence=px.colors.sequential.RdBu,
        )
        fig_toss.update_traces(textposition='inside', textinfo='percent+label')
        fig_toss.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_toss, use_container_width=True)
        
    with col_d:
        st.subheader("🎯 Match Result Types")
        win_types = filtered_matches.apply(
            lambda x: 'Won Batting First' if x['win_by_runs'] > 0 
            else ('Won Chasing' if x['win_by_wickets'] > 0 else 'Tie/No Result'),
            axis=1
        )
        win_type_counts = win_types.value_counts().reset_index()
        win_type_counts.columns = ['Type', 'Count']
        
        fig_win_type = px.pie(
            win_type_counts,
            names='Type',
            values='Count',
            color_discrete_sequence=['#ff9f43', '#0abde3', '#576574'],
            template='plotly_dark',
        )
        fig_win_type.update_traces(textposition='inside', textinfo='percent+label')
        fig_win_type.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_win_type, use_container_width=True)
    
    st.divider()
    
    # Additional insights
    col_e, col_f = st.columns(2)
    
    with col_e:
        st.subheader("🏆 Title Winners")
        if 'season' in filtered_matches.columns:
            # Group by season and get the winner (team with most titles in selected seasons)
            season_winners = filtered_matches.groupby(['season', 'winner']).size().reset_index(name='wins')
            season_winners = season_winners.loc[season_winners.groupby('season')['wins'].idxmax()]
            title_counts = season_winners['winner'].value_counts().reset_index()
            title_counts.columns = ['Team', 'Titles']
            
            fig_titles = px.bar(
                title_counts,
                x='Team',
                y='Titles',
                template='plotly_dark',
                color='Titles',
                color_continuous_scale='YlOrRd',
            )
            fig_titles.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_titles, use_container_width=True)
    
    with col_f:
        st.subheader("📊 Win Percentage (Top Teams)")
        team_stats = []
        for team in teams:
            team_matches = filtered_matches[
                (filtered_matches['team1'] == team) | (filtered_matches['team2'] == team)
            ]
            wins = filtered_matches[filtered_matches['winner'] == team].shape[0]
            total = team_matches.shape[0]
            if total > 0:
                win_pct = (wins / total) * 100
                team_stats.append({'Team': team, 'Win %': win_pct, 'Matches': total})
        
        team_stats_df = pd.DataFrame(team_stats).sort_values('Win %', ascending=False).head(10)
        
        fig_win_pct = px.bar(
            team_stats_df,
            x='Win %',
            y='Team',
            orientation='h',
            template='plotly_dark',
            color='Win %',
            color_continuous_scale='Greens',
            hover_data=['Matches'],
        )
        fig_win_pct.update_layout(
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_win_pct, use_container_width=True)

# ============================================================================
# TAB 2: PLAYER ANALYSIS
# ============================================================================

with tab2:
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.subheader("🏏 Top Run Scorers")
        top_scorers = filtered_deliveries.groupby('batsman')['batsman_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        top_scorers.columns = ['Batsman', 'Runs']
        
        fig_scorers = px.bar(
            top_scorers,
            x='Runs',
            y='Batsman',
            orientation='h',
            template='plotly_dark',
            color='Runs',
            color_continuous_scale='Sunsetdark',
        )
        fig_scorers.update_layout(
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_scorers, use_container_width=True)
        
    with col_p2:
        st.subheader("⚡ Top Wicket Takers")
        valid_dismissals = get_valid_dismissals()
        wicket_takers = filtered_deliveries[
            filtered_deliveries['dismissal_kind'].isin(valid_dismissals)
        ]
        top_wicket_takers = wicket_takers['bowler'].value_counts().head(10).reset_index()
        top_wicket_takers.columns = ['Bowler', 'Wickets']
        
        fig_wicketers = px.bar(
            top_wicket_takers,
            x='Wickets',
            y='Bowler',
            orientation='h',
            template='plotly_dark',
            color='Wickets',
            color_continuous_scale='Teal',
        )
        fig_wicketers.update_layout(
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_wicketers, use_container_width=True)

    st.divider()
    
    col_p3, col_p4 = st.columns(2)
    
    with col_p3:
        st.subheader("💥 Most Sixes")
        six_hitters = filtered_deliveries[filtered_deliveries['batsman_runs'] == 6].groupby('batsman').size().sort_values(ascending=False).head(10).reset_index()
        six_hitters.columns = ['Batsman', 'Sixes']
        
        fig_sixes = px.bar(
            six_hitters,
            x='Sixes',
            y='Batsman',
            orientation='h',
            template='plotly_dark',
            color='Sixes',
            color_continuous_scale='Oranges',
        )
        fig_sixes.update_layout(
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_sixes, use_container_width=True)
    
    with col_p4:
        st.subheader("🎯 Most Fours")
        four_hitters = filtered_deliveries[filtered_deliveries['batsman_runs'] == 4].groupby('batsman').size().sort_values(ascending=False).head(10).reset_index()
        four_hitters.columns = ['Batsman', 'Fours']
        
        fig_fours = px.bar(
            four_hitters,
            x='Fours',
            y='Batsman',
            orientation='h',
            template='plotly_dark',
            color='Fours',
            color_continuous_scale='Blues',
        )
        fig_fours.update_layout(
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_fours, use_container_width=True)
    
    st.divider()
    
    # Player Deep Dive
    st.subheader("🔍 Player Deep Dive")
    
    col_select, col_empty = st.columns([2, 1])
    with col_select:
        player_list = sorted(filtered_deliveries['batsman'].unique())
        selected_player = st.selectbox(
            "Select a player for detailed statistics",
            player_list,
            index=0 if player_list else None
        )
    
    if selected_player:
        player_df = filtered_deliveries[filtered_deliveries['batsman'] == selected_player]
        
        # Calculate stats
        total_runs = int(player_df['batsman_runs'].sum())
        innings = int(player_df['match_id'].nunique())
        balls_faced = int(player_df.shape[0])
        fours = int(player_df[player_df['batsman_runs'] == 4].shape[0])
        sixes = int(player_df[player_df['batsman_runs'] == 6].shape[0])
        strike_rate = calculate_strike_rate(total_runs, balls_faced)
        avg_per_innings = total_runs / innings if innings > 0 else 0
        
        # Display metrics
        metric_cols = st.columns(6)
        metric_cols[0].metric("Total Runs", f"{total_runs:,}")
        metric_cols[1].metric("Innings", innings)
        metric_cols[2].metric("Strike Rate", f"{strike_rate:.1f}")
        metric_cols[3].metric("Avg/Innings", f"{avg_per_innings:.1f}")
        metric_cols[4].metric("Fours", fours)
        metric_cols[5].metric("Sixes", sixes)
        
        st.divider()
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Run distribution
            run_counts = player_df['batsman_runs'].value_counts().reset_index().sort_values('batsman_runs')
            run_counts.columns = ['Runs', 'Frequency']
            
            fig_runs_dist = px.bar(
                run_counts,
                x='Runs',
                y='Frequency',
                title=f"Run Distribution - {selected_player}",
                template='plotly_dark',
                color='Frequency',
                color_continuous_scale='Plasma',
            )
            fig_runs_dist.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_runs_dist, use_container_width=True)
        
        with col_chart2:
            # Runs per season
            player_season_runs = player_df.merge(
                filtered_matches[['id', 'season']],
                left_on='match_id',
                right_on='id',
                how='left'
            ).groupby('season')['batsman_runs'].sum().reset_index()
            player_season_runs.columns = ['Season', 'Runs']
            
            fig_season_runs = px.line(
                player_season_runs,
                x='Season',
                y='Runs',
                title=f"Runs Per Season - {selected_player}",
                template='plotly_dark',
                markers=True,
            )
            fig_season_runs.update_traces(line_color='#ff4b4b', marker=dict(size=8))
            fig_season_runs.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_season_runs, use_container_width=True)

# ============================================================================
# TAB 3: VENUE ANALYSIS
# ============================================================================

with tab3:
    st.subheader("🏟️ Most Hosted Venues")
    
    venue_matches = filtered_matches['venue'].value_counts().head(15).reset_index()
    venue_matches.columns = ['Venue', 'Matches']
    
    fig_venue = px.bar(
        venue_matches,
        x='Matches',
        y='Venue',
        orientation='h',
        template='plotly_dark',
        color='Matches',
        color_continuous_scale='Viridis',
    )
    fig_venue.update_layout(
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig_venue, use_container_width=True)
    
    st.divider()
    
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        st.subheader("📊 High Scoring Venues")
        # Average first innings score per venue
        first_innings = filtered_deliveries[filtered_deliveries['inning'] == 1]
        match_scores = first_innings.groupby('match_id')['total_runs'].sum().reset_index()
        match_venue = filtered_matches[['id', 'venue']].rename(columns={'id': 'match_id'})
        venue_scores = match_scores.merge(match_venue, on='match_id')
        avg_scores = venue_scores.groupby('venue')['total_runs'].mean().sort_values(ascending=False).head(15).reset_index()
        avg_scores.columns = ['Venue', 'Avg Score']
        
        fig_avg_venue = px.bar(
            avg_scores,
            x='Avg Score',
            y='Venue',
            orientation='h',
            template='plotly_dark',
            color='Avg Score',
            color_continuous_scale='Reds',
        )
        fig_avg_venue.update_layout(
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_avg_venue, use_container_width=True)
    
    with col_v2:
        st.subheader("🎯 Winning After Toss")
        # Teams winning after winning toss
        toss_win_matches = filtered_matches[
            filtered_matches['toss_winner'] == filtered_matches['winner']
        ]
        toss_advantage = (len(toss_win_matches) / len(filtered_matches) * 100) if len(filtered_matches) > 0 else 0
        
        toss_impact = pd.DataFrame({
            'Outcome': ['Won After Winning Toss', 'Lost After Winning Toss'],
            'Count': [len(toss_win_matches), len(filtered_matches) - len(toss_win_matches)]
        })
        
        fig_toss_impact = px.pie(
            toss_impact,
            names='Outcome',
            values='Count',
            template='plotly_dark',
            color_discrete_sequence=['#2ecc71', '#e74c3c'],
            hole=0.4,
        )
        fig_toss_impact.update_traces(textposition='inside', textinfo='percent+label')
        fig_toss_impact.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_toss_impact, use_container_width=True)
        
        st.metric("Toss Advantage", f"{toss_advantage:.1f}%")

# ============================================================================
# TAB 4: OVER ANALYSIS
# ============================================================================

with tab4:
    st.subheader("📈 Scoring and Wickets by Over")
    
    # Group by over
    over_stats = filtered_deliveries.groupby('over').agg({
        'total_runs': 'sum',
        'player_dismissed': lambda x: x.notna().sum(),
        'ball': 'count'
    }).reset_index()
    over_stats.columns = ['Over', 'Total Runs', 'Wickets', 'Balls']
    
    # Calculate average runs per over
    over_stats['Avg Runs per Ball'] = over_stats['Total Runs'] / over_stats['Balls']
    
    col_o1, col_o2 = st.columns(2)
    
    with col_o1:
        fig_over_runs = px.line(
            over_stats,
            x='Over',
            y='Total Runs',
            title="Total Runs Scored per Over",
            markers=True,
            template='plotly_dark',
        )
        fig_over_runs.update_traces(line_color='#ff4b4b', marker=dict(size=6))
        fig_over_runs.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_over_runs, use_container_width=True)
    
    with col_o2:
        fig_over_wickets = px.bar(
            over_stats,
            x='Over',
            y='Wickets',
            title="Total Wickets per Over",
            template='plotly_dark',
            color='Wickets',
            color_continuous_scale='Teal',
        )
        fig_over_wickets.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_over_wickets, use_container_width=True)
    
    st.divider()
    
    # Powerplay vs Middle vs Death overs
    st.subheader("⚡ Phase-wise Analysis")
    
    phase_data = filtered_deliveries.copy()
    phase_data['Phase'] = phase_data['over'].apply(
        lambda x: 'Powerplay (1-6)' if x < 6 
        else ('Middle (7-15)' if x < 15 else 'Death (16-20)')
    )
    
    phase_stats = phase_data.groupby('Phase').agg({
        'total_runs': 'sum',
        'player_dismissed': lambda x: x.notna().sum(),
        'ball': 'count'
    }).reset_index()
    
    phase_stats['Economy'] = (phase_stats['total_runs'] / (phase_stats['ball'] / 6)).round(2)
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        fig_phase_runs = px.bar(
            phase_stats,
            x='Phase',
            y='total_runs',
            title="Runs by Match Phase",
            template='plotly_dark',
            color='total_runs',
            color_continuous_scale='Reds',
            labels={'total_runs': 'Total Runs'},
        )
        fig_phase_runs.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_phase_runs, use_container_width=True)
    
    with col_p2:
        fig_phase_economy = px.bar(
            phase_stats,
            x='Phase',
            y='Economy',
            title="Economy Rate by Phase",
            template='plotly_dark',
            color='Economy',
            color_continuous_scale='Greens',
        )
        fig_phase_economy.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_phase_economy, use_container_width=True)

# ============================================================================
# TAB 5: TEAM COMPARISON
# ============================================================================

with tab5:
    st.subheader("🆚 Head-to-Head Analysis")
    
    # Win matrix
    pivot_data = []
    for _, row in filtered_matches.iterrows():
        winner = row['winner']
        if pd.notna(winner):
            loser = row['team2'] if row['team1'] == winner else row['team1']
            if pd.notna(loser):
                pivot_data.append({'Winner': winner, 'Loser': loser})
    
    if pivot_data:
        pivot_df = pd.DataFrame(pivot_data)
        heatmap_data = pd.crosstab(pivot_df['Winner'], pivot_df['Loser'])
        
        fig_heat = px.imshow(
            heatmap_data,
            text_auto=True,
            template='plotly_dark',
            aspect='auto',
            color_continuous_scale='Viridis',
            labels={'x': 'Lost Against', 'y': 'Won By', 'color': 'Wins'},
        )
        fig_heat.update_layout(
            title="Team vs Team Win Matrix",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("📊 Not enough data for head-to-head analysis")
    
    st.divider()
    
    # Team selector for detailed comparison
    st.subheader("🔍 Compare Two Teams")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        team1 = st.selectbox("Select Team 1", teams, key='team1_select')
    
    with col_t2:
        team2 = st.selectbox("Select Team 2", teams, key='team2_select', index=1 if len(teams) > 1 else 0)
    
    if team1 and team2 and team1 != team2:
        # Head to head matches
        h2h_matches = filtered_matches[
            ((filtered_matches['team1'] == team1) & (filtered_matches['team2'] == team2)) |
            ((filtered_matches['team1'] == team2) & (filtered_matches['team2'] == team1))
        ]
        
        team1_wins = h2h_matches[h2h_matches['winner'] == team1].shape[0]
        team2_wins = h2h_matches[h2h_matches['winner'] == team2].shape[0]
        total_h2h = h2h_matches.shape[0]
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(f"{team1} Wins", team1_wins)
        col_m2.metric("Total Matches", total_h2h)
        col_m3.metric(f"{team2} Wins", team2_wins)
        
        # Visualization
        h2h_data = pd.DataFrame({
            'Team': [team1, team2],
            'Wins': [team1_wins, team2_wins]
        })
        
        fig_h2h = px.bar(
            h2h_data,
            x='Team',
            y='Wins',
            template='plotly_dark',
            color='Team',
            color_discrete_sequence=['#ff4b4b', '#0abde3'],
        )
        fig_h2h.update_layout(
            title=f"{team1} vs {team2} - Head to Head",
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_h2h, use_container_width=True)

# ============================================================================
# TAB 6: ADVANCED STATS
# ============================================================================

with tab6:
    st.subheader("🎯 Advanced Insights")
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.subheader("🏆 Most Consistent Teams")
        # Teams with best win percentage (min 20 matches)
        consistency_stats = []
        for team in teams:
            team_matches = filtered_matches[
                (filtered_matches['team1'] == team) | (filtered_matches['team2'] == team)
            ]
            if team_matches.shape[0] >= 10:  # Minimum threshold
                wins = filtered_matches[filtered_matches['winner'] == team].shape[0]
                total = team_matches.shape[0]
                win_pct = (wins / total) * 100
                consistency_stats.append({
                    'Team': team,
                    'Win %': win_pct,
                    'Matches': total,
                    'Wins': wins
                })
        
        consistency_df = pd.DataFrame(consistency_stats).sort_values('Win %', ascending=False).head(10)
        
        fig_consistency = px.scatter(
            consistency_df,
            x='Matches',
            y='Win %',
            size='Wins',
            color='Win %',
            hover_name='Team',
            template='plotly_dark',
            color_continuous_scale='RdYlGn',
            size_max=30,
        )
        fig_consistency.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_consistency, use_container_width=True)
    
    with col_a2:
        st.subheader("📊 Dismissal Types Distribution")
        dismissal_counts = filtered_deliveries['dismissal_kind'].value_counts().reset_index()
        dismissal_counts.columns = ['Dismissal Type', 'Count']
        dismissal_counts = dismissal_counts[dismissal_counts['Dismissal Type'].notna()]
        
        fig_dismissals = px.pie(
            dismissal_counts,
            names='Dismissal Type',
            values='Count',
            template='plotly_dark',
            hole=0.3,
        )
        fig_dismissals.update_traces(textposition='inside', textinfo='percent+label')
        fig_dismissals.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_dismissals, use_container_width=True)
    
    st.divider()
    
    col_a3, col_a4 = st.columns(2)
    
    with col_a3:
        st.subheader("🎪 Extras Conceded by Type")
        extras_data = filtered_deliveries[filtered_deliveries['extra_runs'] > 0]
        
        # Count different types of extras
        extras_breakdown = {
            'Wides': extras_data[extras_data['wide_runs'] > 0].shape[0],
            'No Balls': extras_data[extras_data['noball_runs'] > 0].shape[0],
            'Byes': extras_data[extras_data['bye_runs'] > 0].shape[0],
            'Leg Byes': extras_data[extras_data['legbye_runs'] > 0].shape[0],
        }
        
        extras_df = pd.DataFrame(list(extras_breakdown.items()), columns=['Type', 'Count'])
        
        fig_extras = px.bar(
            extras_df,
            x='Type',
            y='Count',
            template='plotly_dark',
            color='Count',
            color_continuous_scale='Reds',
        )
        fig_extras.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_extras, use_container_width=True)
    
    with col_a4:
        st.subheader("📈 Run Rate Progression")
        # Calculate cumulative run rate by over
        over_cumulative = filtered_deliveries.groupby('over').agg({
            'total_runs': 'sum',
            'ball': 'count'
        }).reset_index()
        
        over_cumulative['Cumulative Runs'] = over_cumulative['total_runs'].cumsum()
        over_cumulative['Cumulative Balls'] = over_cumulative['ball'].cumsum()
        over_cumulative['Run Rate'] = (over_cumulative['Cumulative Runs'] / over_cumulative['Cumulative Balls']) * 6
        
        fig_run_rate = px.line(
            over_cumulative,
            x='over',
            y='Run Rate',
            title="Cumulative Run Rate by Over",
            template='plotly_dark',
            markers=True,
        )
        fig_run_rate.update_traces(line_color='#2ecc71')
        fig_run_rate.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_run_rate, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style='text-align: center; color: #94a3b8; padding: 20px;'>
    <p>🏏 <b>IPL Analytics Dashboard</b> | Data-driven insights into the Indian Premier League</p>
    <p style='font-size: 0.8rem;'>Built with Streamlit & Plotly | Data: IPL Matches & Deliveries</p>
</div>
""", unsafe_allow_html=True)
