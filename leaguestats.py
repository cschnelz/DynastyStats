from customtypes import POSITIONS
import numpy as np
from teams import Team

class LeagueStats:
    def __init__(self):
        self.average_starter_ppg: int
        self.median_starter_ppg: int
        self.average_starters: dict
        self.median_starters: dict
        self.average_best_bench: dict
        self.median_best_bench: dict

    def average_starter_ppg(self):
        return self.average_starter_ppg
        
    def set_average_starter_ppg(self, ppg):
        self.average_starter_ppg = ppg
    
    def median_starter_ppg(self):
        return self.median_starter_ppg
        
    def set_median_starter_ppg(self, ppg):
        self.median_starter_ppg = ppg

    # starter_position
    def average_starter_position_ppg(self, position):
        return self.average_starters[position.name]
        
    def set_average_starter_position_ppg(self, position, ppg):
        self.average_starters[position.name] = ppg
    
    def median_starter_position_ppg(self, position):
        return self.median_starters[position.name]
        
    def set_median_starter_position_ppg(self, position, ppg):
        self.median_starters[position.name] = ppg

    # bench_position
    def average_bench_position_ppg(self, position):
        return self.average_best_bench[position.name]
    
    def set_average_bench_position_ppg(self, position, ppg):
        self.average_best_bench[position.name] = ppg

    def median_bench_position_ppg(self, position):
        return self.median_best_bench[position.name]
    
    def set_median_bench_position_ppg(self, position, ppg):
        self.median_best_bench[position.name] = ppg

    # Boolean_position
    def average_position_ppg(self, position, starter=False, bench=False):
        if starter:
            return self.average_starter_position_ppg(position)
        if bench:
            return self.average_bench_position_ppg(position)
        raise Exception("Must specify either starter or bench")

    def median_position_ppg(self, position, starter=False, bench=False):
        if starter:
            return self.median_starter_position_ppg(position)
        if bench:
            return self.median_bench_position_ppg(position)
        raise Exception("Must specify either starter or bench")

    # Boolean_boolean
    def position_ppg(self, position, starter=False, bench=False, average=False, median=False):
        if average:
            return self.average_position_ppg(position, starter, bench)
        if median:
            return self.median_position_ppg(position, starter, bench)
        raise Exception("Must specify either average or median")

    
def calculate_league_starter_stats(league: list[Team], league_wide_statistics):
    # sum the starter fppg for the roster                           # for every team in the league
    sum_of_starter_ppg_per_team = [sum([row['FPPG'] for i,row in team.get_starters().iterrows()]) for team in league]
    league_wide_statistics['average_starter_ppg'] = np.average(sum_of_starter_ppg_per_team)
    league_wide_statistics['median_starter_ppg'] = np.median(sum_of_starter_ppg_per_team)

    for position in POSITIONS:
        starters = [np.array(team.get_position_starters(position)['FPPG']) for team in league]
        league_wide_statistics['average_starters'][position.name] = [np.nanmean(k) for k in zip(*starters)]
        league_wide_statistics['median_starters'][position.name] = [np.nanmedian(k) for k in zip(*starters)]

def calculate_league_bench_stats(league: list[Team], league_wide_statistics):
    for position in filter(lambda position: position!=POSITIONS.QB, POSITIONS):
        # for the position, get a list of n-deep backup ppg for every team
        bench_players = [np.array(team.get_position_backups(position, count=position.bench_count())['FPPG']) for team in league]
        # take element-wise averages across depth: [ average best backup, average second backup, ...]
        league_wide_statistics['average_best_bench'][position.name] = [np.nanmean(k) for k in zip(*bench_players)]
        league_wide_statistics['median_best_bench'][position.name] = [np.nanmedian(k) for k in zip(*bench_players)]