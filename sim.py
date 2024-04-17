import organism

class sim:

    def __init__(self):

        self.organisms = []

    def randomly_generate_genome(self, steps):
        pass

    def linear_score(self, x):
        return(x)
    
    def generate(self, n):

        for i in range(n):
            self.organisms.append(organism(self))

    def run(self, iterations):

        for i in range(iterations):
            for g in self.organisms:
                g.update_states()
                move = g.get_move()
                print(f"{g.position} + {move}")
                g.position += move 


if __name__ == "__main__":

    s = sim()
    s.generate(1)
    s.run(10)



