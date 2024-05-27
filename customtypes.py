from enum import Enum

class POSITIONS(Enum):
    QB, WR, RB, TE, FLEX, SFLEX = range(6)

    def matched_positions(self):
        if self.name == 'FLEX':
            return ['WR','RB','TE']
        elif self.name == 'SFLEX':
            return ['QB','WR','RB','TE']
        return [self.name]

    def bench_count(self):
        bench_counts = {
            'RB': 2,
            'WR': 2,
            'TE': 1,
            'FLEX': 3,
            'SFLEX': 1,
            'QB': 0
        }
        return bench_counts[self.name]
        
    def starter_count(self):
        start_counts = {
            'RB': 1,
            'WR': 2,
            'TE': 1,
            'FLEX': 2,
            'SFLEX': 1,
            'QB': 1
        }
        return start_counts[self.name]

