from sim import sim
import math
import numpy as np

class static_bot:

    def __init__(self, sim):
        self.sim = sim

        self.sensor_angles = [0., 1./3, 2./3]
        self.sensor_distances = [1, 1, 1]

        self.score = 0
        self.position = [0,0]

    def get_move(self):

        move_x = 0
        move_y = 0
        current_gradient_val = self.sim.gradient_score(self.position[0], self.position[1])

        for i in range(len(self.sensor_angles)):
            theta = self.sensor_angles[i] * 2 * math.pi
            d = self.sensor_distances[i]

            print(f"{theta}\t{d}")
            
            x = d * np.cos(theta)
            y = d * np.sin(theta)

            print(f"x: {x}\ny: {y}")

            gradient_val = self.sim.gradient_score(x, y)
            gradient_diff = gradient_val - current_gradient_val

            print(gradient_val)
            print(gradient_diff)

            delta_x = gradient_diff * np.cos(theta)
            delta_y = gradient_diff * np.sin(theta)

            move_x += delta_x
            move_y += delta_y

        return(move_x, move_y)



if __name__ == "__main__":
    
    simulation = sim()

    bot = static_bot(simulation)
    print(bot.get_move())