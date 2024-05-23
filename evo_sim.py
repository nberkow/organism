import random
import numpy as np
from util import *
from genome_sim import genome_sim
from spawner import spawner
from sim_visualizer import sim_visualizer
from multiprocessing import Pool
from static_bot import static_bot
from genome_bot import genome_bot

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

    def run_round(self, round_number, genomes=[]):

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

        print(len(finished_bots))

        all_stats = summarize_run(finished_bots, raw_genomes_by_bot_name)

        #self.spawner.summarize_and_store_genomes(all_stats)
        #self.sim_visualizer.make_jsons(all_stats, finished_bots, raw_genomes_by_bot_name, "data/round_bots")

        move_log_dict = self.sim_visualizer.round_bots_to_move_log_dict(finished_bots)
        self.sim_visualizer.make_round_report(all_stats, move_log_dict, raw_genomes_by_bot_name, 5, 3, f"figures/round_{round_number}_report.png")
        
        offspring = self.spawner.spawn_next_round(all_stats, self.selection_percent)
        return offspring

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
        bot = genome_bot(name, self.gradient, self.weights, tree, pos)
        return(bot)       


if __name__ == "__main__":

    random.seed(11)
    np.random.seed(11)

    sim = evo_sim(100, 5)
    sim.generate_random_genomes()
    offspring = sim.run_round(0)
    print(len(offspring))

    sim.set_genomes_from_list(offspring)
    offspring = sim.run_round(1)
    print(len(offspring))

    sim.set_genomes_from_list(offspring)
    offspring = sim.run_round(2)
    print(len(offspring))

    sim.set_genomes_from_list(offspring)
    offspring = sim.run_round(3)
    print(len(offspring))
