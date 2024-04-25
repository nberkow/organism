import math
import numpy as np

class static_bot:

    def __init__(self, sim, name, pos=[0,0]):
        self.sim = sim
        self.name = name

        self.sensor_angles = [0., 1./3, 2./3]
        self.sensor_distances = [.01, .01, .01]

        self.score = 0
        self.position = pos

        self.pos_log = {'x' : [self.position[0]],
                        'y' : [self.position[1]],
                        's' : [self.sim.gradient_score(self.position[0], self.position[1])]}

    def get_move(self):

        move_x = 0
        move_y = 0
        current_gradient_val = self.sim.gradient_score(self.position[0], self.position[1])

        for i in range(len(self.sensor_angles)):
            theta = self.sensor_angles[i] * 2 * math.pi
            d = self.sensor_distances[i]

            x = d * np.cos(theta)
            y = d * np.sin(theta)

            gradient_val = self.sim.gradient_score(x, y)
            gradient_diff = gradient_val - current_gradient_val

            delta_x = gradient_diff * np.cos(theta)
            delta_y = gradient_diff * np.sin(theta)

            move_x += delta_x
            move_y += delta_y

        return(move_x, move_y)
    
    def make_move(self):

        dx, dy = self.get_move()
        print(dx, dy)
        self.position = [self.position[0] + dx, self.position[1] + dy]
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        self.pos_log['x'].append(new_x)
        self.pos_log['y'].append(new_y)
        self.pos_log['s'].append(self.sim.gradient_score(new_x, new_y))
