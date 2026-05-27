import time
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams


import nba_api.library.http as nba_http
nba_http.HEADERS = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',
}

# --- Database Connection ---
load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Get teams
all_teams = teams.get_teams()
teams_df = pd.DataFrame(all_teams)

# Get recent lakers games
time.sleep(1) # rate limiting
lakers_gamefinder = leaguegamefinder.Leaguegamefinder(
    team_id_nullable = 1610612747 #Lakers
)
lakers_games_df = lakers_gamefinder.get_data_frames()[0]

# Load into postgres
teams_df.columns = teams_df.columns.str.lower()
teams_df.to_sql("teams", engine, if_exists="replace", index=False)
lakers_games_df.columns = lakers_games_df.columns.str.lower()
lakers_games_df.to_sql("games", engine, if_exists="replace", index=False)

print("Data loaded successfully")

# --- Test query ---
with engine.connect() as conn:
    result = pd.read_sql("""
        SELECT game_date, matchup, wl, pts
        FROM games 
        ORDER BY game_date DESC 
        LIMIT 10
    """, conn)
    print(result)