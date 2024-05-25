import random
import numpy as np
from util import *
from spawner import spawner
from sim_visualizer import sim_visualizer
from multiprocessing import Pool
from static_bot import static_bot
from genome_bot import genome_bot
from scipy.stats import multivariate_normal

class evo_sim:

    def __init__(self, n_genomes, individuals):

        self.genome_sim_iterations = 400
        self.n_genomes = n_genomes

        self.x_range = [-1,1]
        self.y_range = [-1,1]

        # Calculate the gradient used for all sims
        print("building gradients")
        self.gradient_means = 1
        self.gradient, self.weights = self.define_gradient_and_weights(self.gradient_means, self.x_range, self.y_range)

        # Make raw genomes as random character strings
        print("making raw genomes")
        self.raw_genome_length = 1000
        self.min_length = 20
        self.char_freq = [.25, .25, .25, .25]

        self.starting_genomes = []
        self.individuals = individuals
        self.selection_percent = .2

        # track the best scoring genomes across all runs and make new generations
        self.spawner = spawner(self)

        # visualize simulation results
        self.sim_visualizer = sim_visualizer(self)

    def generate_random_genomes(self):
        self.starting_genomes = self.get_random_raw_genomes(self.n_genomes, self.raw_genome_length, self.char_freq, self.min_length)

    def set_genomes_from_list(self, genomes):
        self.starting_genomes = genomes

    def define_gradient_and_weights(self, gradient_means, x_range, y_range):

        """
        Create a gradient as list of weighted bivariate normal distributions

        inputs:
        - x_range - two element list definines the x range where the mean can be placed
        - y_range - two element list definines the y range where the mean can be placed
        - means - the number of means to create, default 1

        outputs:
        - gradient - a list of distribution objects
        - weights - a list of weights summing to one
        """
            
        gradient = []
        weights  = []

        for i in range(gradient_means):
            x_mean = random.random() * (x_range[1] - x_range[0]) + x_range[0]
            y_mean = random.random() * (y_range[1] - y_range[0]) + y_range[0]
            dist = multivariate_normal([x_mean, y_mean])
            gradient.append(dist)

        denom = 0.
        raw = []

        for i in range(gradient_means):
            r = random.random()
            raw.append(r)
            denom += r
        
        for r in raw:
            weights.append(r/denom)

        return(gradient, weights)
    
    
    def make_random_sequence(self, n, p):
        
        characters = ['[',']','0','1']
        s = "".join(np.random.choice(characters, p=p, size=n))
        return(s)
    
    def get_random_raw_genomes(self, n, raw_genome_length, char_freq, min_length):

        g = 0
        t = 0
        genomes = []

        while g < n and t < 10**9:
            raw_seq = self.make_random_sequence(raw_genome_length, char_freq)
            valid_tree = get_functional_genome(raw_seq, [0, len(raw_seq)])
            if len(valid_tree) >= min_length:
                genomes.append(raw_seq)
                g+=1
            t+=1
        return(genomes)

    def run_round(self, round_number, genomes=[], make_figures=False):

        if len(genomes) == 0:
            genomes = self.starting_genomes

        # Run simulations
        print("setting up simulations")
        bots_to_run = []
        raw_genomes_by_bot_name = {}

        i = 0

        for raw_genome in genomes:
            genome = get_functional_genome(raw_genome)
            tree = sequence_to_tree(genome)

            for j in range(self.individuals):
                bot_name = f"b_{i}_{j}"
                b = self.spawn_genome_bot(bot_name, tree)
                raw_genomes_by_bot_name[bot_name] = raw_genome
                bots_to_run.append((b, self.genome_sim_iterations))
            
            i += 1

        print(f"running round with {len(bots_to_run)} bots in parallel")
                
        with Pool(10) as p:
            finished_bots = p.map(run_bot, bots_to_run)
        

        round_stats = summarize_run(finished_bots, raw_genomes_by_bot_name)

        #self.spawner.summarize_and_store_genomes(all_stats)
        #self.sim_visualizer.make_jsons(all_stats, finished_bots, raw_genomes_by_bot_name, "data/round_bots")

        figure_file = None
        if make_figures:
            figure_file = f"figures/round_{round_number}_report.png"
        move_log_dict = self.sim_visualizer.round_bots_to_move_log_dict(finished_bots)

        self.sim_visualizer.make_round_report(round_stats, move_log_dict, raw_genomes_by_bot_name, 5, 3, figure_file)

        stats = ['mean_net_diff', 'mean_best_diff', 'mean_avg_diff']
        bots_for_leaderboard = self.sim_visualizer.get_bots_to_display(stats, round_stats, move_log_dict, raw_genomes_by_bot_name, 20, 3)

        offspring = self.spawner.spawn_next_round(round_stats, self.selection_percent)
        return {"offspring": offspring, 
                "top_scoring_bots_by_stat" : bots_for_leaderboard,
                "genome_by_bot_name" : raw_genomes_by_bot_name}

    def get_random_pos(self):

        xr = self.x_range[1] - self.x_range[0]
        yr = self.y_range[1] - self.y_range[0]

        pos = [
            random.random() * xr - self.x_range[1],
            random.random() * yr - self.y_range[1],
        ]

        return(pos)

    def spawn_static_bot(self, name):
        pos = self.get_random_pos()
        return(static_bot(self.sim, name, pos))

    def spawn_genome_bot(self, name, tree):
        pos = self.get_random_pos()
        twist = random.random()
        bot = genome_bot(name, self.gradient, self.weights, tree, pos, twist)
        return(bot)

class leaderboard:

    def __init__(self):

        self.n = 20
        self.leaders_per_round = []
        self.stats = ['mean_net_diff', 'mean_best_diff', 'mean_avg_diff']

        self.names_by_genome = {}

    def add_round(self, round_num, top_bots_by_stat, genome_by_bot_name):

        round_data = {}
        for stat in self.stats:
            round_data[stat] = []
            already_ranked_genomes = set()
            for i in range(len(top_bots_by_stat[stat])):
                
                b = top_bots_by_stat[stat][i]
                g = genome_by_bot_name[b]
                if not g in already_ranked_genomes:

                    if not g in self.names_by_genome:
                        name = f"g_r{round_num}_p{i}"
                        self.names_by_genome[g] = name
                    else:
                        name = self.names_by_genome[g]

                    already_ranked_genomes.add(g)
                    round_data[stat].append(name)
        
        self.leaders_per_round.append(round_data)

    def write_leader_summary(self, outfile):

        header = ["rank"] + self.stats

        with open(outfile, 'w') as report:
            
            for round in range(len(self.leaders_per_round)):
                print(f"Round {round} Leaders", file=report)
                print("\t".join(header), file=report)
                round_data = self.leaders_per_round[round]
                for i in range(self.n):
                    line_elements = [str(i + 1)]
                    for stat in self.stats:
                        name = round_data[stat][i]
                        line_elements.append(name)
                    print("\t".join(line_elements), file=report)
                print("\n\n", file=report)
                

if __name__ == "__main__":

    random.seed(11)
    np.random.seed(11)
    lboard = leaderboard()

    report_at_round = 2

    round = 0
    sim = evo_sim(2500, 21)
    sim.generate_random_genomes()

    round_results = sim.run_round(round, make_figures=True)
    offspring = round_results['offspring']
    top_bots_by_stat = round_results["top_scoring_bots_by_stat"]
    genome_by_bot_name = round_results["genome_by_bot_name"]
    lboard.add_round(round, top_bots_by_stat, genome_by_bot_name)

    print(f"len offspring: {len(offspring)}")
    print(f"len genome_by_bot_name: {len(genome_by_bot_name)}")

    lboard.write_leader_summary(f"figures/leaderboard_{round}.tsv")
  
    for round in range(1, 20000):

        make_figs = False
        if round == report_at_round:
            make_figs = True

        sim.set_genomes_from_list(offspring)
        round_results = sim.run_round(round, make_figures=make_figs)
        offspring = round_results['offspring']
        top_bots_by_stat = round_results["top_scoring_bots_by_stat"]
        genome_by_bot_name = round_results["genome_by_bot_name"]

        print(f"len offspring: {len(offspring)}")
        print(f"len genome_by_bot_name: {len(genome_by_bot_name)}")

        lboard.add_round(round, top_bots_by_stat, genome_by_bot_name)

        if round == report_at_round * 10:
            lboard.write_leader_summary(f"figures/leaderboard_{round}.tsv")

        if make_figs:
            report_at_round *= 2


