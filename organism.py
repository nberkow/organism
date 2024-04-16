import json

class organism:

    def __init__(self, sim):

        self.sim = sim

        """
        a string that encodes a decision tree. the leave are integers referencing array positions
        """
        self.genome = "[[0][1][2]]"

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
        self.state_starts_and_ends = [[0, len(self.genome)]]
        

        """
        current position
        """
        self.position = 0

    def update_states(self):
        pass

    def get_move(self):
    
        tree = json.loads(self.state)
        move = self.evaluate_tree(tree)

    def evaluate_tree(self, tree):
        """
        recursively evaluate a tree as nested list
        """


    def mutate_and_spawn(self, offspring):
        pass

if __name__ == "__main__":