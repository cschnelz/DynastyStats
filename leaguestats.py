from customtypes import POSITIONS
import numpy as np
from teams import Team

class LeagueStats:
    def __init__(self):
        self.average_starter_ppg: int
        self.median_starter_ppg: int
        self.average_starters = dict()
        self.median_starters = dict()
        self.average_best_bench = dict()
        self.median_best_bench = dict()

    # combined starter
    def average_starter_ppg(self):
        return self.average_starter_ppg
        
    def set_average_starter_ppg(self, ppg):
        self.average_starter_ppg = ppg
    
    def median_starter_ppg(self):
        return self.median_starter_ppg
        
    def set_median_starter_ppg(self, ppg):
        self.median_starter_ppg = ppg

    def starter_ppg(self, average=False, median=False) -> int:
        if average:
            return self.average_starter_ppg
        if median:
            return self.median_starter_ppg
        raise Exception("Must specify either average or median")
    
    def set_starter_ppg(self, ppg: int, average=False, median=False):
        if average:
            self.set_average_starter_ppg(ppg)
        elif median:
            self.set_median_starter_ppg(ppg)
        else:
            raise Exception("Must specify either average or median")

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
    
    def set_average_position_ppg(self, position, ppg, starter=False, bench=False):
        if starter:
            self.set_average_starter_position_ppg(position, ppg)
        elif bench:
            self.set_average_bench_position_ppg(position, ppg)
        else:
            raise Exception("Must specify either starter or bench")

    def set_median_position_ppg(self, position, ppg, starter=False, bench=False):
        if starter:
            self.set_median_starter_position_ppg(position, ppg)
        elif bench:
            self.set_median_bench_position_ppg(position, ppg)
        else:
            raise Exception("Must specify either starter or bench")

    # Boolean_boolean
    def position_ppg(self, position: POSITIONS, starter=False, bench=False, average=False, median=False) -> list[int]:
        if average:
            return self.average_position_ppg(position, starter, bench)
        if median:
            return self.median_position_ppg(position, starter, bench)
        raise Exception("Must specify either average or median")
    
    def set_position_ppg(self, position: POSITIONS, ppg: list[int], starter=False, bench=False, average=False, median=False):
        if average:
            self.set_average_position_ppg(position, ppg, starter, bench)
        elif median:
            self.set_median_position_ppg(position, ppg, starter, bench)
        else:
            raise Exception("Must specify either average or median")

# combined starter ppg and positional starter ppg
def calculate_league_starter_stats(league: list[Team], leagueStats: LeagueStats) -> None:
    sum_of_starter_ppg_per_team = [sum([row['FPPG'] for i,row in team.get_starters().iterrows()]) for team in league]
    leagueStats.set_starter_ppg(np.average(sum_of_starter_ppg_per_team), average=True)
    leagueStats.set_starter_ppg(np.median(sum_of_starter_ppg_per_team), median=True)

    for position in POSITIONS:
        starters = [np.array(team.get_position_starters(position)['FPPG']) for team in league]
        leagueStats.set_position_ppg(position, [np.nanmean(k) for k in zip(*starters)], starter=True, average=True)
        leagueStats.set_position_ppg(position, [np.nanmedian(k) for k in zip(*starters)], starter=True, median=True)

# positional bench ppg
def calculate_league_bench_stats(league: list[Team], leagueStats: LeagueStats) -> None:
    for position in filter(lambda position: position!=POSITIONS.QB, POSITIONS):
        # for the position, get a list of n-deep backup ppg for every team
        bench_players = [np.array(team.get_position_backups(position, count=position.bench_count())['FPPG']) for team in league]
        # take element-wise averages across depth: [ average best backup, average second backup, ...]
        leagueStats.set_position_ppg(position, [np.nanmean(k) for k in zip(*bench_players)], bench=True, average=True)
        leagueStats.set_position_ppg(position, [np.nanmedian(k) for k in zip(*bench_players)], bench=True, median=True)

def calculate_league_starter_stats_depr(league ,league_wide_statistics):
    # sum the starter fppg for the roster                           # for every team in the league
    sum_of_starter_ppg_per_team = [sum([row['FPPG'] for i,row in team.get_starters().iterrows()]) for team in league]
    league_wide_statistics['average_starter_ppg'] = np.average(sum_of_starter_ppg_per_team)
    league_wide_statistics['median_starter_ppg'] = np.median(sum_of_starter_ppg_per_team)

    for position in POSITIONS:
        starters = [np.array(team.get_position_starters(position)['FPPG']) for team in league]
        league_wide_statistics['average_starters'][position.name] = [np.nanmean(k) for k in zip(*starters)]
        league_wide_statistics['median_starters'][position.name] = [np.nanmedian(k) for k in zip(*starters)]

# for every position considered
def calculate_league_bench_stats_depr(league, league_wide_statistics):
    for position in filter(lambda position: position!=POSITIONS.QB, POSITIONS):
        # for the position, get a list of n-deep backup ppg for every team
        bench_players = [np.array(team.get_position_backups(position, count=position.bench_count())['FPPG']) for team in league]
        # take element-wise averages across depth: [ average best backup, average second backup, ...]
        league_wide_statistics['average_best_bench'][position.name] = [np.nanmean(k) for k in zip(*bench_players)]
        league_wide_statistics['median_best_bench'][position.name] = [np.nanmedian(k) for k in zip(*bench_players)]


def normalize_score(score):
    return (score * 100)

# 1, 0.5, 0.25 ...
def get_bench_weights(count):
    return [1 / pow(2,i) for i in range(count)]

# team combined starter score
def calculate_overall_starter_score_for_team(team, league_wide_statistics):
    # sum teams starter ppg             # get the percentage of the league average and normalize
    starter_score_vs_avg = team.get_starters()['FPPG'].sum() / league_wide_statistics['average_starter_ppg']
    starter_score_vs_avg = normalize_score(starter_score_vs_avg)
    starter_score_vs_median = team.get_starters()['FPPG'].sum() / league_wide_statistics['median_starter_ppg']
    starter_score_vs_median = normalize_score(starter_score_vs_median)
    team.scores['starter_score'] = np.average([starter_score_vs_avg, starter_score_vs_median])

# (team: Team, pos: 'Position', starter: boolean, number_of_players_to_score: int)
def calculate_score_for_position(team: Team, league_wide_statistics, position, starter: bool, number_of_players_to_score):
    if starter:
        players = team.get_position_starters(position, count=number_of_players_to_score)['FPPG']
        avgs = league_wide_statistics['average_starters'][position.name]
        medians = league_wide_statistics['median_starters'][position.name]
    else:
        players = team.get_position_backups(position, count=number_of_players_to_score)['FPPG']
        avgs = league_wide_statistics['average_best_bench'][position.name]
        medians = league_wide_statistics['median_best_bench'][position.name]

    # will be a list of ith backup / ith league average backup
    # [ best_backup / league_best_backup, second_backup / league_second_backup, ...]
    vs_avg = np.array(players) / np.array(avgs)
    vs_avg = normalize_score(vs_avg)
    vs_median = np.array(players) / np.array(medians)
    vs_median = normalize_score(vs_median)

    # take an element-wise mean of vs_avg and medians
    # [ mean(best_backup / league_best_avg, best_backup / league_best_median), ...]
    combined = [np.mean([avg, median]) for avg, median in zip(vs_avg, vs_median)]
    
    # take the weighted average of the scores and insert single numeric score
    if starter:
        team.scores['starters'][position.name] = np.average(combined, weights=get_bench_weights(number_of_players_to_score))
    else:
        team.scores['bench'][position.name] = np.average(combined, weights=get_bench_weights(number_of_players_to_score))
