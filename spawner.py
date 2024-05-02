from genome_bot import genome_bot
from static_bot import static_bot
import random
import json
import re
import numpy as np
from util import get_clean_subtree, sequence_to_tree

class spawner:

    def __init__(self, sim):
        self.sim = sim

    def get_random_pos(self):

        xr = self.sim.x_range[1] - self.sim.x_range[0]
        yr = self.sim.y_range[1] - self.sim.y_range[0]

        pos = [
            random.random() * xr - self.sim.x_range[1],
            random.random() * yr - self.sim.y_range[1],
        ]

        return(pos)

    def spawn_static_bot(self, name):

        pos = self.get_random_pos()
        return(static_bot(self.sim, name, pos))

    
    def spawn_genome_bot(self, name):

        pos = self.get_random_pos()
        bot = genome_bot(self.sim, name, pos)
        return(bot)

