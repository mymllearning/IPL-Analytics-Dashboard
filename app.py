import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(page_title="IPL Dashboard", layout="wide", page_icon="🏏")

# --- Custom CSS for Aesthetics ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #41444b;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #ff4b4b;
    }
    .metric-label {
        font-size: 1rem;
        color: #babcbf;
    }
    h1, h2, h3 {
        color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    matches = pd.read_csv("data/matches (1).csv")
    deliveries = pd.read_csv("data/deliveries (2).csv")
    
    # Data Cleaning
    # Fix team names (e.g., Rising Pune Supergiant)
    team_mapping = {
        'Rising Pune Supergiant': 'Rising Pune Supergiants',
        'Delhi Daredevils': 'Delhi Capitals',
        'Deccan Chargers': 'Sunrisers Hyderabad',
        'Pune Warriors': 'Rising Pune Supergiants' # Keeping it simple or merging? Let's genericize or keep separate if meaningful.
        # Actually usually it's better to keep Deccan Chargers separate from SRH as they are different franchises technically, 
        # but for user simplicity often merged. I will normalize distinct spelling errors but maybe keep franchises separate if distinct.
        # 'Rising Pune Supergiant' and 'Rising Pune Supergiants' is a real dup.
    }
    
    matches['team1'] = matches['team1'].replace('Rising Pune Supergiant', 'Rising Pune Supergiants')
    matches['team2'] = matches['team2'].replace('Rising Pune Supergiant', 'Rising Pune Supergiants')
    matches['winner'] = matches['winner'].replace('Rising Pune Supergiant', 'Rising Pune Supergiants')
    matches['toss_winner'] = matches['toss_winner'].replace('Rising Pune Supergiant', 'Rising Pune Supergiants')
    
    # Deliveries team names
    deliveries['batting_team'] = deliveries['batting_team'].replace('Rising Pune Supergiant', 'Rising Pune Supergiants')
    deliveries['bowling_team'] = deliveries['bowling_team'].replace('Rising Pune Supergiant', 'Rising Pune Supergiants')

    return matches, deliveries

matches, deliveries = load_data()

# --- Sidebar Filters ---
st.sidebar.title("🏏 IPL Dashboard")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/8/84/Indian_Premier_League_Official_Logo.svg", width=100) # Placeholder or link

# Season Filter
seasons = sorted(matches['season'].unique())
selected_season = st.sidebar.multiselect("Select Season", seasons, default=seasons)

# Team Filter
teams = sorted(matches['team1'].dropna().unique())
selected_teams = st.sidebar.multiselect("Select Teams", teams, default=teams)

# Filter Data
if selected_season:
    filtered_matches = matches[matches['season'].isin(selected_season)]
else:
    filtered_matches = matches

if selected_teams:
    filtered_matches = filtered_matches[
        (filtered_matches['team1'].isin(selected_teams)) | 
        (filtered_matches['team2'].isin(selected_teams))
    ]

# For deliveries, we need match ids from filtered matches
filtered_match_ids = filtered_matches['id'].unique()
filtered_deliveries = deliveries[deliveries['match_id'].isin(filtered_match_ids)]


# --- KPI Section ---
st.title("🏆 IPL Analytics Dashboard (2008-2024)")

col1, col2, col3, col4 = st.columns(4)

total_matches = filtered_matches.shape[0]
total_runs = filtered_deliveries['total_runs'].sum()
total_wickets = filtered_deliveries['player_dismissed'].count()
total_sixes = filtered_deliveries[filtered_deliveries['batsman_runs'] == 6].shape[0]

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{total_matches}</div><div class="metric-label">Total Matches</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{total_runs:,}</div><div class="metric-label">Total Runs</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{total_wickets:,}</div><div class="metric-label">Total Wickets</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{total_sixes:,}</div><div class="metric-label">Total Sixes</div></div>', unsafe_allow_html=True)

st.divider()

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Match Analysis", "🧑 Player Analysis", "📍 Venue Analysis", "⏱️ Over Analysis", "📊 Heatmaps"])

# --- Tab 1: Match Analysis ---
with tab1:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Matches per Season")
        matches_per_season = filtered_matches['season'].value_counts().sort_index().reset_index()
        matches_per_season.columns = ['Season', 'Matches']
        fig_matches = px.bar(matches_per_season, x='Season', y='Matches', color='Matches', template='plotly_dark', color_continuous_scale='Reds')
        st.plotly_chart(fig_matches, use_container_width=True)
    
    with col_b:
        st.subheader("Wins by Team")
        wins_by_team = filtered_matches['winner'].value_counts().reset_index()
        wins_by_team.columns = ['Team', 'Wins']
        fig_wins = px.bar(wins_by_team, x='Wins', y='Team', orientation='h', template='plotly_dark', color='Wins', color_continuous_scale='Viridis')
        st.plotly_chart(fig_wins, use_container_width=True)

    col_c, col_d = st.columns(2)
    
    with col_c:
        st.subheader("Toss Decision Impact")
        toss_counts = filtered_matches['toss_decision'].value_counts().reset_index()
        fig_toss = px.pie(toss_counts, names='toss_decision', values='count', hole=0.4, template='plotly_dark', color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_toss, use_container_width=True)
        
    with col_d:
        st.subheader("Match Result Type")
        # result_counts = filtered_matches['result'].value_counts().reset_index() # 'result' col might have 'normal', 'tie'
        # To make it interesting: Win by runs vs wickets
        win_types = filtered_matches.apply(lambda x: 'Batting First' if x['win_by_runs'] > 0 else ('Chasing' if x['win_by_wickets'] > 0 else 'Tie/NR'), axis=1)
        win_type_counts = win_types.value_counts().reset_index()
        win_type_counts.columns = ['Type', 'Count']
        fig_win_type = px.pie(win_type_counts, names='Type', values='Count', color_discrete_sequence=['#ff9f43', '#0abde3', '#576574'], template='plotly_dark')
        st.plotly_chart(fig_win_type, use_container_width=True)

# --- Tab 2: Player Analysis ---
with tab2:
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.subheader("Top Must Run Scorers")
        top_scorers = filtered_deliveries.groupby('batsman')['batsman_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_scorers = px.bar(top_scorers, x='batsman_runs', y='batsman', orientation='h', title='Top 10 Run Scorers', template='plotly_dark', color='batsman_runs', color_continuous_scale='Solar')
        st.plotly_chart(fig_scorers, use_container_width=True)
        
    with col_p2:
        st.subheader("Top Wicket Takers")
        # Filter for valid dismissals (excluding run outs presumably, or keep all)
        # dismissal_kind: ['caught', 'bowled', 'run out', 'lbw', 'caught and bowled', 'stumped', 'retired hurt', 'hit wicket', 'obstructing the field']
        # Usually 'run out' and 'retired hurt' don't count to bowler.
        valid_dismissals = ['caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket']
        wicket_takers = filtered_deliveries[filtered_deliveries['dismissal_kind'].isin(valid_dismissals)]
        top_wicket_takers = wicket_takers['bowler'].value_counts().head(10).reset_index()
        top_wicket_takers.columns = ['Bowler', 'Wickets']
        fig_wicketers = px.bar(top_wicket_takers, x='Wickets', y='Bowler', orientation='h', title='Top 10 Wicket Takers', template='plotly_dark', color='Wickets', color_continuous_scale='Teal')
        st.plotly_chart(fig_wicketers, use_container_width=True)

    st.subheader("Player Stats Explorer")
    player_list = sorted(filtered_deliveries['batsman'].unique())
    selected_player = st.selectbox("Select Player for Detailed Stats", player_list)
    
    if selected_player:
        player_df = filtered_deliveries[filtered_deliveries['batsman'] == selected_player]
        runs = player_df['batsman_runs'].sum()
        fours = player_df[player_df['batsman_runs'] == 4].shape[0]
        sixes = player_df[player_df['batsman_runs'] == 6].shape[0]
        innings = player_df['match_id'].nunique() # Approx
        
        st.metric(label="Total Runs", value=runs)
        st.metric(label="Innings Played", value=innings)
        
        # Run distribution
        run_counts = player_df['batsman_runs'].value_counts().reset_index().sort_values('batsman_runs')
        fig_runs_dist = px.bar(run_counts, x='batsman_runs', y='count', title=f"Run Distribution for {selected_player}", template='plotly_dark')
        st.plotly_chart(fig_runs_dist, use_container_width=True)


# --- Tab 3: Venue Analysis ---
with tab3:
    st.subheader("Venue Statistics")
    
    venue_matches = filtered_matches['venue'].value_counts().head(10).reset_index()
    venue_matches.columns = ['Venue', 'Matches']
    
    fig_venue = px.bar(venue_matches, x='Matches', y='Venue', orientation='h', template='plotly_dark', color='Matches')
    st.plotly_chart(fig_venue, use_container_width=True)
    
    # Avg score per venue (First Innings)
    first_innings = filtered_deliveries[filtered_deliveries['inning'] == 1]
    match_scores = first_innings.groupby(['match_id'])['total_runs'].sum().reset_index()
    match_venue = filtered_matches[['id', 'venue']].rename(columns={'id': 'match_id'})
    venue_scores = match_scores.merge(match_venue, on='match_id')
    avg_scores = venue_scores.groupby('venue')['total_runs'].mean().sort_values(ascending=False).head(15).reset_index()
    
    st.subheader("High Scoring Venues (Avg 1st Innings Score)")
    fig_avg_venue = px.bar(avg_scores, x='total_runs', y='venue', orientation='h', template='plotly_dark', color='total_runs')
    st.plotly_chart(fig_avg_venue, use_container_width=True)

# --- Tab 4: Over Analysis ---
with tab4:
    st.subheader("Run Rate & Wickets Per Over")
    
    # Group by over
    over_stats = filtered_deliveries.groupby('over').agg({'total_runs': 'sum', 'player_dismissed': 'count', 'ball': 'count'}).reset_index()
    # Approx match count to normalize? Or just view total distribution
    # Run Rate calculation: Total Runs / (Total Balls / 6) -> approx
    
    fig_over_runs = px.line(over_stats, x='over', y='total_runs', title="Total Runs Scored per Over Number (Across all selected matches)", markers=True, template='plotly_dark')
    st.plotly_chart(fig_over_runs, use_container_width=True)
    
    fig_over_wickets = px.bar(over_stats, x='over', y='player_dismissed', title="Total Wickets Fall per Over Number", template='plotly_dark', color='player_dismissed')
    st.plotly_chart(fig_over_wickets, use_container_width=True)

# --- Tab 5: Heatmaps ---
with tab5:
    st.subheader("Team vs Team Win Heatmap")
    
    # Win Matrix
    # We need a matrix where x=Team1, y=Team2, value=Wins of Team1 against Team2? Or just wins frequency
    # Let's do: Rows = Winner, Cols = Loser
    
    pivot_data = []
    for index, row in filtered_matches.iterrows():
        winner = row['winner']
        loser = row['team2'] if row['team1'] == winner else row['team1']
        if pd.notna(winner) and pd.notna(loser):
            pivot_data.append({'Winner': winner, 'Loser': loser})
            
    if pivot_data:
        pivot_df = pd.DataFrame(pivot_data)
        heatmap_data = pd.crosstab(pivot_df['Winner'], pivot_df['Loser'])
        
        fig_heat = px.imshow(heatmap_data, text_auto=True, template='plotly_dark', aspect='auto', color_continuous_scale='Viridis')
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Not enough data for heatmap")

st.markdown("---")
st.markdown("Created with ❤️ by Antigravity")
