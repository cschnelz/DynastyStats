import pandas as pd
from enum import Enum
from typing import Literal

import copy
from customtypes import POSITIONS

class Team:
    def __init__(self, owner):
        self.owner = owner
        self.contender_strength = 0
        # roster
        self.roster = pd.DataFrame()
        # roster, with starters by projection marked
        self.roster_starters = pd.DataFrame()

        self.starting_roster = {}
        
        self.scores = {
            'starter_score': 0,
            'starters': {},
            'bench': {}  
        }
    def get_starters(self) -> pd.DataFrame:
        return self.roster_starters.query('Starter')

    def get_backups(self) -> pd.DataFrame:
        return self.roster_starters.query('not Starter')

    def get_position_players(self, position: POSITIONS, count=0, index=0) -> pd.DataFrame:
        players = self.roster.query(f'position in {position.matched_positions()}')
        return players.head(count) if count else players
    
    # gets all starters for position. position: String, count: Int (optional, if 0 returns all)
    def get_position_starters(self, position: POSITIONS, count=0, index=-1) -> pd.DataFrame:
        starters = self.starting_roster[position.name]
        starters = starters.head(count) if count else starters
        if index >= 0:
            if index >= starters.shape[0]:
                print(f'RETURNING NAN ROW for {self.owner} {position.name} starters index {index}')
                return pd.DataFrame(columns=starters.columns, index=range(1))
            starters = starters.iloc[index]
        return starters

    # gets all backups for position. position: String
    def get_position_backups(self, position, count=0, index=-1) -> pd.DataFrame:
        backups = self.roster_starters.query(f'not Starter and position in {position.matched_positions()}')
        backups = backups.head(count) if count else backups
        if index >= 0:
            if index >= backups.shape[0]:
                print(f'RETURNING NAN ROW for {self.owner} {position.name} backups index {index}')
                return pd.DataFrame(columns=backups.columns, index=range(1))
            backups = backups.iloc[index]
        return backups

    def combined_starter_score(self):
        return self.scores['starter_score']

    def position_starter_score(self, position: POSITIONS):
        return self.scores['starters'][position.name]
    
    def position_bench_score(self, position: POSITIONS):
        return self.scores['bench'][position.name]

def build_league(rosters: pd.DataFrame, players: pd.DataFrame, projections: pd.DataFrame, ktc: pd.DataFrame, fantasy_calc: pd.DataFrame) -> list[Team]:
  league = []
  for index,roster in rosters.iterrows():
    team = Team(roster['owner'])
    # dataframe with column of player_id, merge to players for name
    team.roster = pd.DataFrame({'player_id': roster['players']})
    team.roster = team.roster.merge(players, how='left')
    # merge to projections and value tables on name
    team.roster = team.roster.merge(projections, how='left')
    team.roster = team.roster.merge(ktc, how='left')
    team.roster = team.roster.merge(fantasy_calc, how='left')
    # sort, calculate ppg, copy into roster_starters table
    team.roster = team.roster.sort_values(by=['FPTS'],ascending=False)
    team.roster['FPPG'] = round(team.roster['FPTS'] / 17.0, 2)
    team.roster.drop(columns=['player_id'],inplace=True)
    team.roster = team.roster.reset_index(drop=True)
    team.roster_starters = team.roster.copy()
    team.roster_starters['Starter'] = False

    league.append(team)
  return league


def set_team_starters(team: Team):
  for position in POSITIONS:
      # find indexes of players in position
      position_indices = team.get_position_backups(position).index
      # take n top projected players where n is the positions starter count definition
      starter_position_indices = position_indices[0: position.starter_count()]
      # mark those players as starters
      team.starting_roster[position.name] = team.roster_starters.loc[starter_position_indices].copy()
      team.roster_starters.loc[starter_position_indices,'Starter'] = True

def copy_team(team: Team) -> Team:
    copied = copy.deepcopy(team)
    copied.roster_starters['Starter'] = False
    return copied
