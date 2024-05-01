from genome_bot import genome_bot
from static_bot import static_bot
import random
import json
import re
import numpy as np

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

    def sequence_to_tree(self, s):

        def parse_inner_list(s, index):
            result = []
            num = ''
            while index < len(s):
                char = s[index]
                if char.isdigit():
                    num += char
                elif char == '[':
                    sublist, index = parse_inner_list(s, index + 1)
                    result.append(sublist)
                elif char == ']':
                    if num:
                        result.append(int(num, 2))
                        num = ''
                    return result, index
                elif char == ',':
                    if num:
                        result.append(int(num, 2))
                        num = ''
                index += 1
            return result, index

        result, _ = parse_inner_list(s, 0)
        return result
    
    def spawn_genome_bot(self, genome, name):

        pos = self.get_random_pos()
        tree = self.sequence_to_tree(genome)
        bot = genome_bot(self.sim, name, pos, genome, tree)
        return(bot)

