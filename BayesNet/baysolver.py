import probability
from itertools import combinations_with_replacement, permutations

class Sensor:

    def __init__(self, r, tpr, fpr):
        self.room = r
        self.idx = None
        self.tpr = float(tpr)
        self.fpr = float(fpr)


class Room:

    def __init__(self, name, idx):
        self.name = name
        self.idx = idx
        self.conns_idx = []
    

class Problem:

    def __init__(self, fh):
        lines = fh.readlines()
        self.room_names = lines[0].strip().split()[1:]
        self.connections = [i.split(",") for i in lines[1].strip().split()[1:]]
        self.connections = [(self.room_names.index(c1), self.room_names.index(c2)) for c1,c2 in self.connections]
        self.rooms = [Room(v, i) for i,v in enumerate(self.room_names)] #Room('name', idx)

        for c1, c2 in self.connections:
            self.rooms[c1].conns_idx.append(c2)
            self.rooms[c2].conns_idx.append(c1)
        
        for r in self.rooms:
            r.conns_idx.append(r.idx)

        self.sensors = {i[0] : Sensor(*i[1:]) for i in [j.split(":") for j in lines[2].strip().split()[1:]] }
        for s in self.sensors.values():
            s.idx = self.room_names.index(s.room)

        self.P = float(lines[3].split()[1])
        self.measurements = { t + 1 : [i.split(":") for i in s.strip().split()[1:]] for t, s in enumerate(lines[4:]) }

        self.N = len(self.room_names)
        self.M = len(self.measurements[1])
        self.T = len(self.measurements)

        self.evidence = {}
        for t in range(1, self.T + 1):
            for s, m in self.measurements[t]:
                var = s + "t" + str(t)
                self.evidence[var] = m == "T"

    def gen_net(self):

        nodes = []

        for i, r in enumerate(self.room_names):
            X = r + "1"
            parents = ""
            p = 0.5 # The problem says "no prior information"
            nodes.append((X, parents, p))

        for t in range(1, self.T):
            for r in range(self.N):
                X = self.room_names[r] + str(t + 1)
                parents = " ".join([self.room_names[r] + str(t) for r in self.rooms[r].conns_idx])

                combs = combinations_with_replacement([True, False], len(self.rooms[r].conns_idx))
                perms = [item for comb in combs for item in permutations(comb)]
                p = {i : 0 for i in perms}

                for i in perms:
                    if any(i):
                        p[i] = self.P
                    
                    if i[-1]:
                        p[i] = 1

                nodes.append((X, parents, p))

        for t in range(1, self.T + 1):
            for j in range(self.M):
                sens_name = self.measurements[t][j][0]
                sens = self.sensors[sens_name]
                parents = sens.room + str(t)

                node_name = sens_name + "t" + str(t)

                cpt = {True : sens.tpr, False: sens.fpr}
                nodes.append((node_name, parents, cpt))
        
        self.net = probability.BayesNet(nodes)
    def solve(self):
        self.gen_net()
        self.print_all()

        cpts = [(n, probability.elimination_ask(n + str(self.T), self.evidence, self.net)[True]) for n in self.room_names]


        ml = max(cpts, key=lambda x: x[1])
        

        ml = (self.room_names[cpts.index(ml)], ml[1])
        print("Most likely final time step:", ml)
        return ml
    
    def print_all(self):
        for t in range(1, self.T + 1):
            for n in self.room_names:
                var = n + str(t)
                print(var, end=":")
                print(probability.elimination_ask(var, self.evidence, self.net)[True])


    
def solver(input_file):
    return Problem(input_file).solve()

def main():
    with open("example.txt", "r") as f:
        print(solver(f))

if __name__ == "__main__":
    main()