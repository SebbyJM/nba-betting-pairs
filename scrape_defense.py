# scrape_defense.py (fixed clearly with abbreviations)
import requests
import pandas as pd
from bs4 import BeautifulSoup
import io

url = 'https://www.basketball-reference.com/leagues/NBA_2025_ratings.html'
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table', {'id': 'ratings'})
df_defense = pd.read_html(io.StringIO(str(table)), header=1)[0]

# Keep correct columns
df_defense = df_defense[['Team', 'DRtg']]

# Clearly mapping full names to abbreviations
team_abbr = {
    'Atlanta Hawks': 'ATL', 'Boston Celtics': 'BOS', 'Brooklyn Nets': 'BKN',
    'Charlotte Hornets': 'CHA', 'Chicago Bulls': 'CHI', 'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL', 'Denver Nuggets': 'DEN', 'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW', 'Houston Rockets': 'HOU', 'Indiana Pacers': 'IND',
    'LA Clippers': 'LAC', 'Los Angeles Lakers': 'LAL', 'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA', 'Milwaukee Bucks': 'MIL', 'Minnesota Timberwolves': 'MIN',
    'New Orleans Pelicans': 'NOP', 'New York Knicks': 'NYK', 'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI', 'Phoenix Suns': 'PHX',
    'Portland Trail Blazers': 'POR', 'Sacramento Kings': 'SAC', 'San Antonio Spurs': 'SAS',
    'Toronto Raptors': 'TOR', 'Utah Jazz': 'UTA', 'Washington Wizards': 'WAS'
}

df_defense['TEAM'] = df_defense['Team'].map(team_abbr)
df_defense.rename(columns={'DRtg': 'DEF RTG'}, inplace=True)
df_defense['DEF RTG RANK'] = df_defense['DEF RTG'].rank(ascending=True).astype(int)

df_defense = df_defense[['TEAM', 'DEF RTG', 'DEF RTG RANK']]

# Save clearly to CSV
df_defense.to_csv('defensive_ratings.csv', index=False)

print("✅ Defensive ratings CSV now uses abbreviations!")
