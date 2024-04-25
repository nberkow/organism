import organism
from static_bot import static_bot
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import multivariate_normal

class sim:

    def __init__(self):

        self.organisms = []

        self.gradient = multivariate_normal([0.5, -0.2], [[2.0, 0.3], [0.3, 1.5]])
        self.fig = go.Figure()

    def add_countour(self, x_range=[-1,1], y_range=[-1,1], steps=100):

        x_abs = x_range[1] - x_range[0]
        y_abs = y_range[1] - y_range[0]

        x_vals = []
        y_vals = []
        first = True

        z = []
        for i in range(steps):
            row = []
            x = (x_abs/steps) * i + x_range[0]
            x_vals.append(x)
            for j in range(steps):
                y = (y_abs/steps) * j + y_range[0]
                p = self.gradient.pdf([x, y])
                row.append(p)
                if first:
                    y_vals.append(y)
            first = False
            z.append(row)
        
        self.fig.add_trace(go.Contour(x=x_vals, y=y_vals, z=z))
        self.fig.show()

    def add_organism(self, organism):
        self.organisms.append(organism)

    def gradient_score(self, x, y):
        return(self.gradient.pdf([x,y]))

    def run(self, iterations):

        for i in range(iterations):
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
                        size=15,
                        angleref="previous",
                    ),
                    name=g.name,
                )
            )

        self.fig.show()


if __name__ == "__main__":

    s = sim()
    s.add_countour()

    b = static_bot(s, "static_bot_1", [-0.5, -0.5])
    s.add_organism(b)
    s.run(100)
    s.plot_paths()

    #for v in range(len(b.pos_log['x'])):
    #    print(f"{b.pos_log['x'][v]}\t{b.pos_log['y'][v]}\t{b.pos_log['s'][v]}")




