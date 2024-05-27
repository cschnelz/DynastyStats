import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd

suffixes = [' Jr.',' II',' III', ' Sr.']

def request_players():
  return requests.get("https://api.sleeper.app/v1/players/nfl")

def get_players(players_response):
  # convert to DF
  players = pd.DataFrame.from_dict(players_response.json()).transpose()
  # cut to columns cared about and normalize names
  players_reduced = players[['position','age','player_id','full_name']]
  players_reduced = players_reduced.rename(columns={'full_name':'Player'})
  players_reduced['Player'] = players_reduced['Player'].str.lower()
  return players_reduced


### rosters_response: ['taxi', 'starters', 'settings', 'roster_id', 'reserve', 'players','player_map', 'owner_id', 'metadata', 'league_id', 'keepers','co_owners']
def request_rosters():
  return requests.get('https://api.sleeper.app/v1/league/1089971282461954048/rosters')

def get_rosters(rosters_response):
  rosters = pd.DataFrame.from_dict(rosters_response.json())

  # add username to roster
  def get_username(owner_id):
    username = requests.get(f'https://api.sleeper.app/v1/user/{owner_id}')
    return username.json()['username']

  rosters['owner'] = rosters['owner_id'].apply(get_username)
  return rosters


### projections_response: ['Player', 'REC', 'YDS', 'TDS', 'ATT', 'YDS', 'TDS', 'FL', 'FPTS']
def request_projections():
  projections_response = dict()
  for pos in ['qb','wr','rb','te']:
    url = f'https://www.fantasypros.com/nfl/projections/{pos}.php?week=draft&scoring=HALF&week=draft'
    html = pd.read_html(url, header=0)
    projections_response[pos] = html[0]
  return projections_response

def get_projections(projections_reponse):
  def clean_player_name(name):
    # names come in with suffix <TEAM>, remove it
    clean = name.split(' ')
    clean = clean[0:-1]
    clean = ' '.join(clean)
    # remove suffixes
    for suffix in suffixes:
      clean = clean.removesuffix(suffix)
    return clean.lower()

  projections_full = pd.DataFrame()
  for pos in ['qb','wr','rb','te']:
    projections = projections_reponse[pos]
    # reset index (data comes in with headers on row 0)
    projections.columns = projections.iloc[0]
    projections = projections.drop(projections.index[0])
    # calculate qb increased scoring
    projections['FPTS'] = projections['FPTS'].astype(float)
    if pos == 'qb':
      projections.columns = ['Player', 'ATT', 'CMP', 'P_YDS', 'TDS', 'INTS', 'ATT', 'R_YDS', 'TDS', 'FL', 'FPTS']
      projections['FPTS'] = (projections['FPTS'] + projections['P_YDS'].astype(float) * 0.0125).round(2)
    # calculate te premium
    if (pos == 'te'):
      projections['FPTS'] = projections['FPTS'] + (projections['REC'].astype(float) / 2)
    # cut to columns cared about and normalize names
    projections = projections[['Player','FPTS']]
    projections['Player'] = projections['Player'].apply(clean_player_name)
    projections_full = pd.concat([projections_full,projections])
  return projections_full


### ktc_response: ['Player Name', 'Position Rank', 'Position', 'Team', 'Value', 'Age','Rookie']
def request_ktc():
    # universal vars
    URL = "https://keeptradecut.com/dynasty-rankings?page={0}&filters=QB|WR|RB|TE|RDP&format=0"
    all_elements = []
    players = []

    # find all elements with class "onePlayer"
    for page in tqdm(range(10), desc="Linking to keeptradecut.com's SF rankings...",unit="page"):
        page = requests.get(URL.format(page))
        soup = BeautifulSoup(page.content, "html.parser")
        player_elements = soup.find_all(class_="onePlayer")
        for player_element in player_elements:
            all_elements.append(player_element)

    # player information
    for player_element in all_elements:

        # find elements within the player container
        player_name_element = player_element.find(class_="player-name")
        player_position_element = player_element.find(class_="position")
        player_value_element = player_element.find(class_="value")
        player_age_element = player_element.find(class_="position hidden-xs")

        # extract player information
        player_name = player_name_element.get_text(strip=True)
        team_suffix = (player_name[-3:] if player_name[-3:] == 'RFA' else player_name[-4:] if player_name[-4] == 'R' else player_name[-2:] if player_name[-2:] == 'FA' else player_name[-3:] if player_name[-3:].isupper() else "")

        # remove the team suffix
        player_name = player_name.replace(team_suffix, "").strip()
        player_position_rank = player_position_element.get_text(strip=True)
        player_value = player_value_element.get_text(strip=True)
        player_value = int(player_value)
        player_position = player_position_rank[:2]

        # handle NoneType for player_age_element
        if player_age_element:
            player_age_text = player_age_element.get_text(strip=True)
            player_age = float(player_age_text[:4]) if player_age_text else 0
        else:
            player_age = 0

        # split team and rookie
        if team_suffix[0] == 'R':
            player_team = team_suffix[1:]
            player_rookie = "Yes"
        else:
            player_team = team_suffix
            player_rookie = "No"

        if player_position == "PI":
            pick_info = {
                "Player Name": player_name,
                "Position Rank": None,
                "Position": player_position,
                "Team": None,
                "Value": player_value,
                "Age": None,
                "Rookie": None
            }
            players.append(pick_info)

        else:
            player_info = {
                "Player Name": player_name,
                "Position Rank": player_position_rank,
                "Position": player_position,
                "Team": player_team,
                "Value": player_value,
                "Age": player_age,
                "Rookie": player_rookie
            }
            players.append(player_info)

    return players

def clean_name_ktc(name):
  if name == "Marquise Brown":
    name = "Hollywood Brown"
  if name == "Gabriel Davis":
    name = "Gabe Davis"
  for suffix in suffixes:
    name = name.removesuffix(suffix)
  return name.lower()

def get_ktc_values(ktc_response):
  # convert ktc scrape to DF
  ktc = pd.DataFrame(ktc_response)
  # cut to columns cared about and normalize
  ktc = ktc.rename(columns={'Player Name':'Player', 'Value': 'KTC_Value'})
  ktc = ktc[['Player','KTC_Value']]
  ktc['Player'] = ktc['Player'].apply(clean_name_ktc)
  return ktc


### fantasy_calc_response: ['player', 'value', 'overallRank', 'positionRank', 'trend30Day',
#       'redraftDynastyValueDifference', 'redraftDynastyValuePercDifference',
#       'redraftValue', 'combinedValue', 'maybeMovingStandardDeviation',
#       'maybeMovingStandardDeviationPerc',
#       'maybeMovingStandardDeviationAdjusted', 'displayTrend', 'maybeOwner',
#       'starter', 'maybeTier', 'maybeAdp', 'maybeTradeFrequency']

def request_fantasy_calc():
  return requests.get("https://api.fantasycalc.com/values/current?isDynasty=true&numQbs=2&numTeams=12&ppr=0.5").json()

def get_fantasy_calc_values(fantasy_calc_response):
  def extract_name(row):
    row['player'] = row['player']['name']
    return row

  fantasy_calc = pd.DataFrame(fantasy_calc_response)
  # player is a dictionary, replace it with just the name
  fantasy_calc = fantasy_calc.apply(extract_name,axis=1)
  # cut to columns cared about and normalize names
  fantasy_calc['player'] = fantasy_calc['player'].apply(clean_name_ktc)
  fantasy_calc = fantasy_calc.rename(columns={'player':'Player','value':'FantasyCalc_Value'})
  fantasy_calc = fantasy_calc[['Player','FantasyCalc_Value','redraftValue','redraftDynastyValueDifference','redraftDynastyValuePercDifference']]
  return fantasy_calc


