import math
import numpy as np
from util import gradient_score

class genome_bot:

    def __init__(self, name, gradient, weights, tree, pos=[0,0]):

        self.name = name

        self.sensor_angles = [0., 1./3, 2./3]
        self.sensor_distances = [.1, .1, .1]

        self.score = 0
        self.position = pos
        self.tree = tree
        self.gradient = gradient
        self.weights = weights

        self.pos_log = {'x' : [self.position[0]],
                        'y' : [self.position[1]],
                        's' : [gradient_score(self.gradient, self.weights, self.position[0], self.position[1])]}

    def evaluate_tree(self, tree, values):
        """
        recursively evaluate a tree as nested list
        - the value of a list is the sum mod 1 of all the elements
        - leaves contain integers. the value of a leaf is the value element at that positions

        e.g.
        values = [0.5, 0.6]
        tree = [[0], [[1],[0]]]
 
        sublists:
        [0] = 0.5
        [[1],[0]] = (0.6 + 0.5) % 1 = 0.1

        full calculation:
        (0.5 + 0.1) % 1 = 0.6
        """

        sum = 0
        if type(tree) == int:
            sum += values[tree % len(values)]
        elif type(tree) == list:
            for e in tree:
                sum += self.evaluate_tree(e, values)
        return(sum % 1)
    
    def get_move(self):

        current_gradient_val = gradient_score(self.gradient, self.weights, self.position[0], self.position[1])
        sensor_values = []

        for i in range(len(self.sensor_angles)):
            theta = self.sensor_angles[i] * 2 * math.pi
            d = self.sensor_distances[i]

            x = d * np.cos(theta) + self.position[0]
            y = d * np.sin(theta) + self.position[1]

            gradient_val = gradient_score(self.gradient, self.weights, x, y)
            gradient_diff = gradient_val - current_gradient_val
            sensor_values.append(gradient_diff)

        values = self.sensor_angles + self.sensor_distances + sensor_values
        rho = self.evaluate_tree(self.tree, values) * 2 * math.pi

        move_x = .01 * np.cos(rho)
        move_y = .01 * np.sin(rho)
        return(move_x, move_y)
    
    def make_move(self):

        dx, dy = self.get_move()
        
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        self.position = [new_x, new_y]
        self.pos_log['x'].append(new_x)
        self.pos_log['y'].append(new_y)
        self.pos_log['s'].append(gradient_score(self.gradient, self.weights, new_x, new_y))




