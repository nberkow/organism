from spawner import spawner

import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import multivariate_normal

class sim:

    def __init__(self, x_range=[-1,1], y_range=[-1,1]):

        self.organisms = []
        self.x_range = x_range
        self.y_range = y_range

        self.gradient = multivariate_normal([0.5, -0.2], [[2.0, 0.3], [0.3, 1.5]])
        self.fig = go.Figure()

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
                p = self.gradient.pdf([x, y])
                row.append(p)
                if first:
                    x_vals.append(x)
            first = False
            z.append(row)
        
        self.fig.add_trace(go.Contour(x=x_vals, y=y_vals, z=z))
        #self.fig.show()

    def add_organism(self, organism):
        self.organisms.append(organism)

    def gradient_score(self, x, y):
        return(self.gradient.pdf([x,y]))

    def run(self, iterations):

        for i in range(iterations):
            print(f"step {i}")
            for g in self.organisms:
                g.make_move()

    def plot_paths(self):

        for g in self.organisms:
            self.fig.add_trace(
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

        self.fig.show()


if __name__ == "__main__":

    s = sim()
    w = spawner(s)

    s.add_countour()

    for i in range(10):
        b = w.spawn_static_bot(f"static_bot_{i}")
        s.add_organism(b)

    s.run(500)
    s.plot_paths()

    #for b in s.organisms:
    #    for v in range(len(b.pos_log['x'])):
    #        print(f"{b.pos_log['x'][v]}\t{b.pos_log['y'][v]}\t{b.pos_log['s'][v]}")




