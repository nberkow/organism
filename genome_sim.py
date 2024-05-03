from spawner import spawner
from util import *
import random
import plotly.graph_objects as go


class genome_sim:

    def __init__(self, name, index, raw_genome, gradient, weights, x_range=[-1,1], y_range=[-1,1]):

        self.name = name
        self.index = index
        self.organisms = []
        self.x_range = x_range
        self.y_range = y_range

        self.gradient = gradient
        self.weights = weights

        self.raw_genome = raw_genome
        self.genome = get_clean_subtree(raw_genome)
        self.tree = sequence_to_tree(self.genome)

        self.top_scorers = []

    def run(self, iterations):

        for i in range(iterations):
            for g in self.organisms:
                g.make_move()

    def add_organism(self, organism):
        self.organisms.append(organism)

    def select_top_scorers(self, top_n=100):

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


    def plot_paths(self, gradient, fname):

        gradient_fig = make_countour_plot(gradient, weights, x_range, y_range)

        for g in self.top_scorers:
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

        gradient_fig.write_image(f"figures/{fname}.png")

    def plot_score_curves(self, org_list, fname):

        curve_fig = go.Figure()
        for b in org_list:
            line_obj = go.Scatter(
                x=list(range(len(b.pos_log['s']))), 
                y=b.pos_log['s'], 
                mode='lines', name=b.name)
            curve_fig.add_trace(line_obj)

        curve_fig.write_image(f"figures/{fname}.png")
