import math
import numpy as np

class static_bot:

    def __init__(self, sim, name, pos=[0,0]):
        self.sim = sim
        self.name = name

        self.sensor_angles = [0., 1./3, 2./3]
        self.sensor_distances = [.1, .1, .1]

        self.score = 0
        self.position = pos

        self.pos_log = {'x' : [self.position[0]],
                        'y' : [self.position[1]],
                        's' : [self.sim.gradient_score(self.position[0], self.position[1])]}

    def get_move(self):

        move_x = 0
        move_y = 0
        current_gradient_val = self.sim.gradient_score(self.position[0], self.position[1])

        print(f"move from:\t{self.position[0]}\t{self.position[1]}")

        for i in range(len(self.sensor_angles)):
            theta = self.sensor_angles[i] * 2 * math.pi
            d = self.sensor_distances[i]

            x = d * np.cos(theta) + self.position[0]
            y = d * np.sin(theta) + self.position[1]

            gradient_val = self.sim.gradient_score(x, y)
            gradient_diff = gradient_val - current_gradient_val

            #print(f"{x:.02}\t{y:.02}\t{gradient_val:.06}\t{gradient_diff:.06}")

            delta_x = gradient_diff * np.cos(theta)
            delta_y = gradient_diff * np.sin(theta)

            #print(f"grad diff: {gradient_diff:.06}\nangle %: {self.sensor_angles[i]}")
            #print(f"dx: {delta_x:.02}\ndy: {delta_y:.02}")

            move_x += delta_x
            move_y += delta_y

        #print(f"move x: {move_x:.02}\nmove y: {move_y:.02}")
        return(move_x, move_y)
    
    
    def make_move(self):

        dx, dy = self.get_move()
        
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        self.position = [new_x, new_y]
        self.pos_log['x'].append(new_x)
        self.pos_log['y'].append(new_y)
        self.pos_log['s'].append(self.sim.gradient_score(new_x, new_y))
