import random
from util import *
from genome_sim import genome_sim
from spawner import spawner
from multiprocessing import Pool

class evo_sim:

    def __init__(self):

        random.seed(11)

        self.x_range = [-1,1]
        self.y_range = [-1,1]

        # Calculate re-usable gradient
        print("building gradients")
        self.gradients_means = 1
        self.gradient, self.weights = define_gradient_and_weights(self.x_range, self.y_range, self.gradients_means)

        # Make raw genomes as random character strings
        print("making raw genomes")
        self.starting_genomes = get_random_raw_genomes(20)
        self.individuals = 10

    def plot_gradient(self):
        gradient_fig = make_countour_plot(self.gradient, self.weights, self.x_range, self.y_range)
        gradient_fig.write_image(f"figures/gradient_alone.png")

    def run_one_genome_sim(self, s):

        s.run(400)
        s.select_top_scorers(20)

        run_stats = summarize_run(s.organisms)
        run_stats['name'] = s.name
        run_stats['index'] = s.index
        print(f"done: {s.name}")

        return(run_stats)

    def run_round(self, round_num=0, genomes=[]):

        if len(genomes) == 0:
            genomes = self.starting_genomes

        # Build a list of simulations ready to be run
        print("setting up simulations")
        i = 0
        simulations = []
        for raw_genome in genomes:
            name = f"simulation_{i}"
            if i % 100 == 0:
                print(name)

            s = genome_sim(name, i, raw_genome, self.gradient, self.weights)
            w = spawner(s)
            for j in range(self.individuals):
                b = w.spawn_genome_bot(f"genome_bot_{i}_{j}")
                s.add_organism(b)
            simulations.append(s)

            i += 1
        
        # Run simulations in parallel
        print("running in parallel")
        with Pool(10) as p:
            run_results = p.map(self.run_one_genome_sim, simulations)

        all_stats = {}
        for run_stats in run_results:
            all_stats[run_stats["name"]] = run_stats

        plot_run_summary(all_stats, "all_stats")

        survivors = select_surviving_simulations(all_stats)
        #for g in survivors:
            
            #s.plot_paths(gradient, survivors[s].name)
        #plot_run_summary(survivors, "survivors")

if __name__ == "__main__":

    sim = evo_sim()
    sim.run_round()