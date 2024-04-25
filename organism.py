import json

class organism:

    def __init__(self, sim):

        self.sim = sim

        """
        a string that encodes a decision tree. the leave are integers referencing array positions
        """
        self.genome = "[[0][1][10]]"

        """
        sensors - relative positions to sample the underlying function
        """

        self.sensor_positions = [-1, 1]
        """
        sum of score function values across all time points
        """
        self.score = 0

        """
        state variables
        """
        self.state = [0.5]
        self.state_subtree_coords = [[0, len(self.genome)]]

        """
        current position
        """
        self.position = 0

    def update_states(self):
        pass

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


    def get_move(self):

        # (future) get sensor positions and state coords from genome

        # collect sensor values
        sensor_vals = []
        for s in self.sensor_positions:
            sensor_vals.append(self.sim.linear_score(self.position + s))
        current_vals = sensor_vals + self.state

        # update states
        new_state_vals = []
        for c in self.state_subtree_coords:
            subtree = self.get_clean_subtree(c)
            new_state_vals.append(self.evaluate_tree(subtree, current_vals))

        #move = self.evaluate_tree(tree)

    def evaluate_int_as_bin(self, v):
        return(str(v),2)

    def evaluate_tree(self, tree, values):
        """
        recursively evaluate a tree as nested list
        - the value of a list is the sum mod 1 of all the elements
        - leaves contain integers. the value of a leaf is the value element at that positions

        e.g.
        values = [0.5,0.6]
        tree = [[0],[[1],[0]]]

        sublists:
        [0] = 0.5
        [[1],[0]] = (0.6 + 0.5) % 1 = 0.1

        full calculation:
        (0.5 + 0.1) % 1 = 0.6
        """

        sum = 0
        for e in tree:
            if type(e) == int:
                b = self.evaluate_int_as_bin(e)
                sum += values[tree[b % len(tree)]]
            elif type(e) == list:
                sum += self.evaluate_tree(e)
        return(sum % 1)

    def mutate_and_spawn(self, offspring):
        pass


if __name__ == "__main__":

    g = organism(None)
    #print(g.get_clean_subtree('][[1][0]]', [1,7]))

