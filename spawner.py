from genome_bot import genome_bot
from static_bot import static_bot
import random
import json

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

    def sequence_to_tree(self, sequence):
        
        t = sequence.replace("][", "],[")
        t = t.replace("1[", "1,[")
        t = t.replace("1[", "0,[")
        t = t.replace("]1", "],1")
        t = t.replace("]0", "],0")
        tree = json.loads(t)
        return(tree)
    
    def get_clean_subtree(self, sequence, coords):

        """
        get the largest fully enclosed sublist
        """

        if not coords[1] - coords[0] > 1 or coords[1] > len(sequence):
            return('[]')

        rough_subseq = '[' + sequence[coords[0]:coords[1]] + ']'              
        stack_heights = {}  # track running differences of opens and closes
        substr_ends   = {}  # track the index where each stack becomes empty

        # iterate over the sequences, updating each potential subsequence
        for i in range(len(rough_subseq)):

            # create a new potential start for an open bracket
            if rough_subseq[i] == '[':
                stack_heights[i] = 0

            # update existing stacks
            for h in stack_heights:
                to_remove = []

                # If the current character is an open bracket 
                if rough_subseq[i] == '[':  
                    stack_heights[h] += 1

                # If the current character is an close bracket
                if rough_subseq[i] == ']':
                    stack_heights[h] -= 1
                    if stack_heights[h] == 0:
                        to_remove.append(h)
                        substr_ends[h] = i + 1

            # clean up finished stacks
            for h in to_remove:
                stack_heights.pop(h, None)

        max_len = 0
        max_len_substr = ''
        for s in substr_ends:
            if max_len < substr_ends[s] - s:
                max_len = substr_ends[s] - s
                max_len_substr = rough_subseq[s:substr_ends[s]]
        return(max_len_substr)

