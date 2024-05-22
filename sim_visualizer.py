import plotly.graph_objects as go
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

    def make_round_report(self, round_stats, move_log_dict):
        for s in move_log_dict:
            print(s)

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
    
    vis = sim_visualizer(None)
    vis.make_round_report(bot_stats, move_logs)
    