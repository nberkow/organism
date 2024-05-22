from util import *

class genome_sim:

    def __init__(self, evo_sim, name, index, raw_genome):

        """
        Simulate multipe organisms with the same genome, starting from different positions

        raw genome - a random string containing characters "1","0","[","]"
        genome - a subtring of the raw genome with balanced brackets
        tree - a nested list representation of the genome
        
        """

        self.evo_sim = evo_sim

        self.name = name
        self.index = index
        self.organisms = []

        self.raw_genome = raw_genome


        self.top_scorers = []

    def add_organism(self, organism):
        self.organisms.append(organism)

    def select_top_scorers(self, top_n=100):

        """
        Select the top scoring individual bots
        """

        organisms_by_score_diff = {}

        for g in self.organisms:
            scores = g.pos_log['s']
            starting_score = scores[0]
            final_score = scores[-1]
            score_diff = final_score - starting_score
            if not score_diff in organisms_by_score_diff:
                organisms_by_score_diff[score_diff] = []
            organisms_by_score_diff[score_diff].append(g)

        diffs = list(organisms_by_score_diff.keys())
        diffs.sort(reverse=True)
        i = 0

        while len(self.top_scorers) < top_n and i < len(diffs):
            self.top_scorers = self.top_scorers + organisms_by_score_diff[diffs[i]]
            i += 1


