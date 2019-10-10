class ASARProblem:
    def actions(s): #returns a list (or a generator) of operators applicable to state s
        return list

    def result(s, a): #returns the state resulting from applying action a to state s
        return newState

    def goal_test(s): #return True if state s is a goal state, and False otherwise

        return (goal_state == s)

    def path_cost(s): #returns the path cost of state s
        return path_cost

    def heuristic(n): #returns the heuristic of node(state) n
        return heuristic


    def load(f): #loads a problem from a file object f
        airports = []
        aircraft_class = []
        airplane = []
        leg = []
        file = open(f, 'r')
        for line in file:
            if line[0] == 'A':
                airports.append(line[1:])
            elif line[0] == 'C':
                aircraft_class.append(line[1:])
            elif line[0] == 'P':
                airplane.append(line[1:])
            elif line[0] == 'L':
                leg.append(line[1:])

        file.close()
        return airports, aircraft_class, airplane, leg

    def save(f,s): #saves a solution state s to a file object f
        return something

aport, acc, aplane, leg = ASARProblem.load('example.txt')
print('Airports: ',  aport, 'Aircraf class: ', acc, aplane, leg)