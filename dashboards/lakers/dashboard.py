import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

# --- Connect Database ---
try:
    engine = create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    with engine.connect() as conn:
        games_df = pd.read_sql("SELECT * FROM games ORDER BY game_date DESC", conn)
    st.success("Connected to database!")
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# --- Load Data ---
with engine.connect() as conn:
    games_df = pd.read_sql("SELECT * FROM games ORDER BY game_date DESC", conn)
    annual_ppg_df = pd.read_sql("""
        SELECT RIGHT(season_id::text, 4) as season_year, AVG(pts) as annual_ppg
        FROM games
        GROUP BY season_year
        ORDER BY season_year ASC
    """, conn)
# --- Dashboard Layout ---
st.title("NBA Dashboard")
st.subheader("Los Angeles Lakers Game Log")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Games Played", len(games_df))
col2.metric("Wins", len(games_df[games_df['wl'] == 'W']))
col3.metric("Losses", len(games_df[games_df['wl'] == 'L']))
col4.metric("Win Percentage", round((len(games_df[games_df['wl'] == 'W'])) / len(games_df), 3))

# --- Sesason PPG Chart ---     
st.subheader('Points Per Game Over Time')
fig = px.line(
    annual_ppg_df,
    x='season_year',
    y='annual_ppg',
    labels={'season_year': 'Season', 'annual_ppg': 'Points Per Game'},
    markers=True
)
st.plotly_chart(fig, width = 'stretch')

# --- Game Log Table ---
st.subheader("Recent Games")
st.dataframe(
    games_df[['game_date', 'matchup', 'wl', 'pts', 'reb', 'ast']].head(20),
    use_container_width=True
)