import probability
class Problem:
    def __init__(self, fh):
        # Place here your code to load problem from opened file object fh
        # and use probability.BayesNet() to create the Bayesian network
        self.measurements = []
        self.room_state = []
        for line in fh:
            line = line.strip().split(' ')
            if line[0] == 'R':
                self.rooms = tuple(line[1:])
            elif line[0] == 'C':
                self.connections = tuple(line[1:])
            elif line[0] == 'S':
                self.sensors = tuple(line[1:])
            elif line[0] == 'P':
                self.P = float(line[1:][0])
            elif line[0] == 'M':
                self.measurements.append(tuple(line[1:]))

        print(self.rooms, '\n', self.connections, '\n', self.sensors, '\n', self.P, '\n', self.measurements)
        T, F = True, False
        fire = probability.BayesNet([
            ('pre_fire', ''),
            ('sensor', ''),
            ('adj_rooms', ''),
            ('Fire', 'pre_fire sensor adj_room',
             {(F, F, F): 0.9,
              (F, F, T): 0.94,
              (F, T, F): 0.29,
              (F, T, T): 0.001,
              (T, F, F): 1.,
              (T, F, T): 1.,
              (T, T, F): 1.,
              (T, T, T): 1.}),
            ])

        pass
    def solve(self):
        # Place here your code to determine the maximum likelihood solution
        # returning the solution room name and likelihood
        # use probability.elimination_ask() to perform probabilistic inference
        room, likelihood = 0, 0
        return (room, likelihood)

def solver(input_file):
    return Problem(input_file).solve()

file = open('example.txt', 'r')
problem = Problem(file)