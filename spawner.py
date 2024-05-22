from genome_bot import genome_bot
from static_bot import static_bot
import random
import json
import re
import numpy as np


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
                    "p_substitution" : 0,
                    "p_copy_paste"   : 0,
                    "p_tandem_dupe"  : 0,
                    "p_del"          : 0,
                    "p_avg_seg_len"  : 0,
                }
        else:
            self.mutation_params = mut_params


    def summarize_and_store_genomes(self, round_summary_data):
        print("-----")
        print("FIXME: spawn logic here")
        print(round_summary_data)
        print("-----")

    
    def mutate(genome, n, mutation_params={}):
        pass
    
    def spawn_next_round(self):
        pass

