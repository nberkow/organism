import plotly.graph_objects as go
from plotly.subplots import make_subplots
from util import *
import json


class sim_visualizer:

    def __init__(self, evo_sim):
        self.evo_sim = evo_sim

        self.gradient_trace = None
        if evo_sim:
            self.gradient_trace = self.make_countour_trace(
                evo_sim.gradient,
                evo_sim.weights,
                evo_sim.x_range,
                evo_sim.y_range,
            )

        self.colors = ['red', 'blue', 'green', 'purple', 'orange', "pink", "lightblue"]



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

    def make_round_report(self, round_stats, move_log_dict, genome_by_bot_name, n, m, fname):

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
        fig = make_subplots(rows=3, cols=3, subplot_titles=stats)

        # Histogram


        for c in range(3):
            hist_go = self.make_histogram(round_stats, stats[c])
        
            fig.add_trace(
                hist_go, row=1, col=c+1
            )


        # Select bots to display in score curves and xy path plots
        top_scoring_bots_by_stat = self.get_bots_to_display(stats, round_stats, move_log_dict, genome_by_bot_name, n, m)
        all_top_scoring_bots = set()

        for stat in top_scoring_bots_by_stat:
            all_top_scoring_bots = all_top_scoring_bots.union(set(top_scoring_bots_by_stat[stat]))

        # get conistant colors for each genome
        color_by_genome = self.get_bot_colors(all_top_scoring_bots, genome_by_bot_name)

        
        # score curves
        for c in range(3):
            s = stats[c]
            top_scoring_bots = top_scoring_bots_by_stat[s]
            traces = self.get_score_curve_traces(top_scoring_bots, move_log_dict, genome_by_bot_name, color_by_genome)
            for tr in traces:
                fig.add_trace(tr, row=2, col=c+1)

        # xy paths
        x_range = [-1,1]
        y_range = [-1,1]

        if self.evo_sim:
            x_range = self.evo_sim.x_range
            y_range = self.evo_sim.y_range

        for c in range(3):
            s = stats[c]
            top_scoring_bots = top_scoring_bots_by_stat[s]
            if self.gradient_trace:
                fig.add_trace(self.gradient_trace, row=3, col=c+1)
            traces = self.get_xy_path_traces(top_scoring_bots, move_log_dict, genome_by_bot_name, color_by_genome)
            for tr in traces:
                fig.add_trace(tr, row=3, col=c+1)

        fig.update_xaxes(range=x_range, row=3)
        fig.update_yaxes(range=y_range, row=3)
        fig.update_layout(showlegend=False)

        fig.write_image(fname)

        return(top_scoring_bots_by_stat)

    def get_bots_to_display(self, stats, round_stats, move_log_dict, genome_by_bot_name, n, m):

        """
        Choose bots to appear in the score traces and gradient paths

        return a dictionary of bot name lists indexed by the statistic used to choose them
        """

        bots_by_genome = self.reverse_genome_bot_dict(genome_by_bot_name)
        top_scoring_bots_by_stat = {}

        for s in stats:
            top_scoring_bots_by_stat[s] = []

        for c in range(3):
            s = stats[c]
            top_scorers = get_top_scoring_genomes(round_stats, s, n)
            for g in top_scorers:
                bot_names = bots_by_genome[g]
                top_scoring_bots = self.get_top_scoring_bots(bot_names, move_log_dict, s, m)
                top_scoring_bots_by_stat[s] += top_scoring_bots

        return top_scoring_bots_by_stat


    def get_bot_colors(self, bot_list, genome_by_bot_name):

        color_index = 0
        color_by_genome = {}

        for b in list(bot_list):
            genome = genome_by_bot_name[b]
            if not genome in color_by_genome:
                if color_index < len(self.colors):
                    color_by_genome[genome] = self.colors[color_index]
                    color_index += 1
                else:
                    color_by_genome[genome] = "grey"
                    
        return color_by_genome
        

    def make_histogram(self, round_stats, stat):

        """
        Make a histogram across all genomes of a given stat
        
        """

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
            'mean_net_diff'  :  get_net_diff,
            'mean_best_diff' :  get_best_diff,
            'mean_avg_diff'  :  get_avg_diff
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


    def make_countour_trace(self, gradient, weights, x_range, y_range, steps=100):

        """
        create a contour plot representing a gradient

        return the plot object
        
        """

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
        
        contour_trace = go.Contour(x=x_vals, y=y_vals, z=z, contours_coloring='heatmap')
        return(contour_trace)

    def get_score_curve_traces(self, selected_bot_names, move_log_dict, genome_by_bot_name, color_by_genome):

        traces = []
        for b in selected_bot_names:
            score_history = move_log_dict[b]['s']
            genome_color = color_by_genome[genome_by_bot_name[b]]
            line_obj = go.Scatter(
                x=list(range(len(score_history))), 
                y=score_history, 
                mode='lines', name=b, line_color=genome_color)
            traces.append(line_obj)

        return(traces)
    
    def get_xy_path_traces(self, selected_bot_names, move_log_dict, genome_by_bot_name, color_by_genome):

        traces = []
        for b in selected_bot_names:
            genome_color = color_by_genome[genome_by_bot_name[b]]
            line_obj = go.Scatter(
                x=move_log_dict[b]['x'], 
                y=move_log_dict[b]['y'], 
                mode='lines+markers', 
                marker=dict(
                        symbol="arrow-bar-up",
                        size=1,
                        angleref="previous",
                    ),
                name=b, line_color=genome_color)
            traces.append(line_obj)

        return(traces)


if __name__ == "__main__":

    with open("data/move_logs.json", 'r') as m:
        move_logs = json.load(m)
    
    with open("data/bot_stats.json", 'r') as s:
        bot_stats = json.load(s)

    with open("data/round_bots_genome_botname.json") as g:
        genome_by_bot_name = json.load(g)
    
    vis = sim_visualizer(None)
    vis.make_round_report(bot_stats, move_logs, genome_by_bot_name, 5, 3, "figures/round_report.png")
    