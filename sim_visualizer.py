import plotly.graph_objects as go
from plotly.subplots import make_subplots
from util import *
import json


class sim_visualizer:

    def __init__(self, evo_sim):
        self.evo_sim = evo_sim

    def round_bots_to_move_log_dict(self, round_bots):

        move_log_dict = {}
        for bot in round_bots:
            move_log_dict[bot.name] = bot.pos_log
        return(move_log_dict)

    def make_jsons(self, round_stats, round_bots, genome_by_bot_name, json_pfx=None):
        
        move_log_dict = self.round_bots_to_move_log_dict(round_bots)

        if json_pfx:
            with open(f"{json_pfx}_move_logs.json", 'w') as j:
                json.dump(move_log_dict, j)

            with open(f"{json_pfx}_stats.json", 'w') as j:
                json.dump(round_stats, j)

            with open(f"{json_pfx}_genome_botname.json", 'w') as j:
                json.dump(genome_by_bot_name, j)

    def make_round_report(self, round_stats, move_log_dict, genome_by_bot_name, n, m):

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
            
            move_log_dict - Nested dictionary. The keys are individual bot names
                
                values dictionary of coordinates and scores.
                    x : [x values]
                    y : [y values]
                    s : [gradient scores at that postion]

            genome_by_bot_name - dict. keys are bot names. vals are genomes

        Output:
            multi-plot figure

            a - Histograms of the 3 score metrics across all genomes

            Make plots for the best n genomes by each of the three metrics

                b - xy traces over gradient of top m bots for each genome. one color per genome
                c - score curves for the genomes selected for a

        """

        
        stats = ['mean_net_diff', 'mean_best_diff', 'mean_avg_diff']

        """
        fig = make_subplots(rows=1, cols=3, subplot_titles=stats)

        for c in range(3):
            hist_go = self.make_histogram(round_stats, stats[c])
        
            fig.add_trace(
                hist_go, row=1, col=c+1
            )

        fig.show()
        """
        
        bots_by_genome = self.reverse_genome_bot_dict(genome_by_bot_name)

        for s in stats[0:1]:
            top_scorers = self.get_top_scoring_genomes(round_stats, s, n)
            for g in top_scorers:
                print(g[1:100])
                bot_names = bots_by_genome[g]
                top_scoring_bots = self.get_top_scoring_bots(bot_names, move_log_dict, s, 5)
                for b in top_scoring_bots:
                    print(f"\t{b}")


    def make_histogram(self, round_stats, stat):

        x = []

        for g in round_stats:
            x.append(round_stats[g][stat])

        hist_go = go.Histogram(x=x)
        return(hist_go)

    def reverse_genome_bot_dict(self, genome_by_bot_name):

        bots_by_genome = {}

        for b in genome_by_bot_name:
            g = genome_by_bot_name[b]
            if not g in bots_by_genome:
                bots_by_genome[g] = []
            bots_by_genome[g].append(b)
        
        return(bots_by_genome)
       
    def get_top_scoring_bots(self, bot_names, move_log_dict, stat, m):
        
        """
        return a list of the best scoring bots to be used in example plots

        inputs:
            bot_names      -  names of set of bots
            move_log_dict  -  x, y and score values indexed by bot name
            stat           -  the stat to use for ranking
            m              -  the number of bots to return

        """

        stat_functions = {
            'mean_net_diff'  :  self.get_net_diff,
            'mean_best_diff' :  self.get_best_diff,
            'mean_avg_diff'  :  self.get_avg_diff
        }

        bots_by_score = {}
        top_scoring = []

        for b in bot_names:
            gradient_vals = move_log_dict[b]['s']
            score = stat_functions[stat](gradient_vals)
            if not score in bots_by_score:
                bots_by_score[score] = []
            bots_by_score[score].append(b)

        ordered_values = sorted(list(bots_by_score.keys()))

        i = 0
        while i < len(ordered_values) and len(top_scoring) < m:
            tied_genomes = bots_by_score[ordered_values[i]]
            j = 0
            while j < len(tied_genomes) and len(top_scoring) < m:
                top_scoring.append(tied_genomes[j])
                j+=1
            i+=1

        return(top_scoring)


    def get_net_diff(self, scores):
        return scores[-1] - scores[0]
    
    def get_best_diff(self, scores):
        return max(scores) - scores[0]
        
    def get_avg_diff(self, scores):
        return np.average(scores) - scores[0]
    
    def get_top_scoring_genomes(self, round_stats, stat, n):

        """
        select the the top n genomes for the given stat
        """

        top_scoring = []
        
        genome_by_stat = {}
        for g in round_stats:
            data_val = round_stats[g][stat]
            if not data_val in genome_by_stat:
                genome_by_stat[data_val] = []
            genome_by_stat[data_val].append(g)
        
        ordered_values = sorted(list(genome_by_stat.keys()))

        i = 0
        while i < len(ordered_values) and len(top_scoring) < n:
            tied_genomes = genome_by_stat[ordered_values[i]]
            j = 0
            while j < len(tied_genomes) and len(top_scoring) < n:
                top_scoring.append(tied_genomes[j])
                j+=1
            i+=1

        return(top_scoring)

    def plot_score_curves(self):

        org_list = self.top_scorers[0:min(20, len(self.top_scorers))]

        curve_fig = go.Figure()
        for b in org_list:
            print(b.pos_log)
            line_obj = go.Scatter(
                x=list(range(len(b.pos_log['s']))), 
                y=b.pos_log['s'], 
                mode='lines', name=b.name)
            curve_fig.add_trace(line_obj)

        curve_fig.write_image(f"figures/{self.name}_score_curves.png")

    def plot_gradient(self, f_dest):
        gradient_fig = self.make_countour_plot(
            self.evo_sim.gradient, 
            self.evo_sim.weights, 
            self.evo_sim.x_range, 
            self.evo_sim.y_range)
        gradient_fig.write_image(f_dest)
    
    def plot_paths(self, genome_sim):

        gradient_fig = self.make_countour_plot(self.gradient, self.weights, self.x_range, self.y_range)
        org_list = genome_sim.top_scorers[0:min(20, len(genome_sim.top_scorers))]

        for g in org_list:
            gradient_fig.add_trace(
                go.Scatter(
                    x=g.pos_log['x'],
                    y=g.pos_log['y'],
                    mode="lines+markers",
                    marker=dict(
                        symbol="arrow-bar-up",
                        size=3,
                        angleref="previous",
                    ),
                    name=g.name,
                )
            )

        gradient_fig.write_image(f"figures/{genome_sim.name}_paths.png")

    def make_countour_plot(self, gradient, weights, x_range, y_range, steps=100):

        """
        create a contour plot representing a gradient

        return the plot object
        
        """

        gradient_fig = go.Figure()
        x_abs = x_range[1] - x_range[0]
        y_abs = y_range[1] - y_range[0]

        x_vals = []
        y_vals = []
        first = True

        z = []
        for i in range(steps):
            row = []
            y = (y_abs/steps) * i + y_range[0] 
            y_vals.append(y)
            for j in range(steps):
                x = (x_abs/steps) * j + x_range[0]
                p = gradient_score(gradient, weights, x, y)
                row.append(p)
                if first:
                    x_vals.append(x)
            first = False
            z.append(row)
        
        gradient_fig.add_trace(go.Contour(x=x_vals, y=y_vals, z=z, contours_coloring='heatmap'))
        return(gradient_fig)
    
    
    def plot_run_summary(self, run_stats, name):

        fig = go.Figure()
        for r in run_stats:

            stats = run_stats[r]
            y_vals = [stats["mean_diff"], stats["mean_max"]]
            y_std  = [stats["std_diff"], stats["std_max"]]

            fig.add_trace(go.Bar(
                name=r,
                x=['y = Avg - Starting', 'y = Best - Starting'], y=y_vals,
                error_y=dict(type='data', array=y_std)
            ))

        fig.update_layout(barmode='group')
        fig.write_image(f"figures/summary_{name}.png")

if __name__ == "__main__":

    with open("data/move_logs.json", 'r') as m:
        move_logs = json.load(m)
    
    with open("data/bot_stats.json", 'r') as s:
        bot_stats = json.load(s)

    with open("data/round_bots_genome_botname.json") as g:
        genome_by_bot_name = json.load(g)
    
    vis = sim_visualizer(None)
    vis.make_round_report(bot_stats, move_logs, genome_by_bot_name, 3, 5)
    