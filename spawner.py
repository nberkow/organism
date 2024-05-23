from util import *
import numpy as np
import random


class spawner:

    def __init__(self, evo_sim, mut_params={}):
        self.evo_sim = evo_sim

        # track genomes by their scores
        self.all_genomes = []

        self.genomes_by_best_final = {}
        self.best_final_keys = []

        self.genomes_by_best_average = {}
        self.best_average_keys = []

        self.genomes_by_best_max = {}
        self.best_max_keys = {}

        # next round params
        self.top_percent = 0.37

        if mut_params == {}:
            self.mutation_params = {
                    "p_tandem_dupe"  : 0.1,
                    "p_del"          : 0.1,
                    "point_mut"      : 1.5,
                    "avg_seg_len"    : 10,
                    "var_seg_len"    : 30,
                }
        else:
            self.mutation_params = mut_params

    
    def spawn_next_round(self, round_stats, top_percent=0.2, mut_params=None):

        """
        Inputs:
            round_stats - Nested dictionary. The keys are raw genome strings (e.g. "[011]0[11][[11]11[00[0[...")

                values - dictionary of stats.
                
                each of these is a measure of how close each bot got to a local maximum averaged across all bots with the
                the same genome

                'mean_net_diff'  - diff between starting gradient value and ending
                'mean_best_diff' - diff between starting gradient value and best value reached during its life
                'mean_avg_diff'  - diff between starting gradient value and its average value over its life

                there are also std vals for each of these (e.g. "std_net_diff")

            mean_offspring_per_genome - how many genomes to make for each selected genome. modified by scores
            mut_params - overrides class values. these params set mutation behavior
        """

        stats = ['mean_net_diff', 'mean_best_diff', 'mean_avg_diff']
        total_genomes = len(round_stats)

        if not mut_params:
            mut_params = self.mutation_params

        n = top_percent * total_genomes
        spawn_number = (total_genomes - n)/n 

        print(f"input genomes:\t{total_genomes}\n" + \
              f"top %:\t\t{top_percent}\n" + \
              f"n:\t\t{n}\n" + \
              f"spawm_number:\t{spawn_number}\n"
              )

        parent_genomes = []
        for stat in stats:
            parent_genomes += get_top_scoring_genomes(round_stats, stat, n/len(stats))

        print(f"parents:\t{len(parent_genomes)}")

        offspring_genomes = []
        for g in parent_genomes:
            offspring_genomes += self.mutate_and_spawn(g, spawn_number, mut_params)

        print(f"offspring:\t{len(offspring_genomes)}")

        return parent_genomes + offspring_genomes

    def mutate_and_spawn(self, parent_genome, spawn_number, mut_params):

        offspring = set()
        while len(offspring) < spawn_number:

            offspring_genome = parent_genome

            if random.random() < mut_params["p_tandem_dupe"]:
                offspring_genome = self.tandem_dupe(offspring_genome, mut_params["avg_seg_len"], mut_params["var_seg_len"])
            if random.random() < mut_params["p_del"]:
                offspring_genome = self.tandem_dupe(offspring_genome, mut_params["avg_seg_len"], mut_params["var_seg_len"])

            offspring_genome = self.add_point_mut(offspring_genome, mut_params["point_mut"])
            offspring.add(offspring_genome)

        return(list(offspring))


    def tandem_dupe(self, genome, avg_seg_len, var_seg_len):

        pos = int(len(genome) * random.random())

        size = int(np.random.normal(avg_seg_len, var_seg_len))

        left_bound = max(0, int(pos - size/2))
        right_bound = min(int(pos + size/2), len(genome)-1)

        left_region = genome[0:left_bound]
        right_region = genome[right_bound:]
        dupe_region = genome[left_bound:right_bound]

        return left_region + dupe_region + dupe_region + right_region
    
    def deletion(self, genome, avg_seg_len, var_seg_len):

        pos = int(len(genome) * random.random())

        size = int(np.random.normal(avg_seg_len, var_seg_len))

        left_bound = max(0, int(pos - size/2))
        right_bound = min(int(pos + size/2), len(genome)-1)

        left_region = genome[0:left_bound]
        right_region = genome[right_bound:]

        return left_region + right_region

    def add_point_mut(self, genome, point_mut_per_genome):

        alphabet = ['[', ']', '1', '0']
        mutated = ""

        point_mut_freq = point_mut_per_genome/len(genome)
        for c in genome:
            if random.random() < point_mut_freq:
                mutated += random.choice(alphabet)
            else:
                mutated += c

        return mutated






        


        

