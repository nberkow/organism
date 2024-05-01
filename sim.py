from spawner import spawner
from util import get_clean_subtree, make_random_sequence, get_random_genomes
import random
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import multivariate_normal

class sim:

    def __init__(self, name, x_range=[-1,1], y_range=[-1,1], seed=11):

        self.name = name
        self.organisms = []
        self.x_range = x_range
        self.y_range = y_range

        random.seed(seed)

        self.gradient = []
        self.weights = []
        self.define_gradient_and_weights()

        self.gradient_fig = go.Figure()
        self.curve_fig = go.Figure()

    def define_gradient_and_weights(self, means=1):

        for i in range(means):
            x_mean = random.random() * (self.x_range[1] - self.x_range[0]) + self.x_range[0]
            y_mean = random.random() * (self.y_range[1] - self.y_range[0]) + self.y_range[0]
            print(f"{x_mean}\t{y_mean}")
            dist = multivariate_normal([x_mean, y_mean])
            self.gradient.append(dist)

        denom = 0.
        raw = []

        for i in range(means):
            r = random.random()
            raw.append(r)
            denom += r
        
        for r in raw:
            self.weights.append(r/denom)
        print(self.weights)

    def add_countour(self, steps=100):

        x_abs = self.x_range[1] - self.x_range[0]
        y_abs = self.y_range[1] - self.y_range[0]

        x_vals = []
        y_vals = []
        first = True

        z = []
        for i in range(steps):
            row = []
            y = (y_abs/steps) * i + self.y_range[0] 
            y_vals.append(y)
            for j in range(steps):
                x = (x_abs/steps) * j + self.x_range[0]
                p = self.gradient_score(x, y)
                row.append(p)
                if first:
                    x_vals.append(x)
            first = False
            z.append(row)
        
        self.gradient_fig.add_trace(go.Contour(x=x_vals, y=y_vals, z=z, contours_coloring='heatmap'))
        self.gradient_fig.write_image("figures/gradient_alone.png")

    def add_organism(self, organism):
        self.organisms.append(organism)

    def gradient_score(self, x, y):

        score = 0
        for i in range(len(self.gradient)):
            score += self.gradient[i].pdf([x,y]) * self.weights[i]
        return(score)

    def run(self, iterations):

        for i in range(iterations):
            if i % 100 == 0:
                print(f"round {i}")

            for g in self.organisms:
                g.make_move()

    def get_organisms_to_plot(self, top_n=100):

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

        to_plot = []
        while len(to_plot) < top_n:
            to_plot = to_plot + organisms_by_score_diff[diffs[i]]
            i += 1

        return(to_plot)

    def plot_paths(self, org_list, fname):

        for g in org_list:
            self.gradient_fig.add_trace(
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

        self.gradient_fig.write_image(f"figures/{fname}.png")

    def plot_score_curves(self, org_list, fname):
        for b in org_list:
            line_obj = go.Scatter(
                x=list(range(len(b.pos_log['s']))), 
                y=b.pos_log['s'], 
                mode='lines', name=b.name)
            self.curve_fig.add_trace(line_obj)

        self.curve_fig.write_image(f"figures/{fname}.png")

if __name__ == "__main__":

    genomes = get_random_genomes(5)
    summary = []
    i = 0

    for g in genomes:
        print(f"trying:\n{g}")

        sim_summary = {"genome" : g}

        s = sim(f"simulation_{i}")
        s.add_countour()

        w = spawner(s)

        for j in range(100):
            b = w.spawn_genome_bot(g, f"genome_bot_{i}_{j}")
            s.add_organism(b)

        s.run(20)
        top_scorers = s.get_organisms_to_plot(10)

        s.plot_paths(top_scorers, f"sim_{i}_gradient")
        s.plot_score_curves(top_scorers, f"sim_{i}_score_curves")

        i += 1







