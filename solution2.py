"""
Artificial Intelligence and Decision Systems
Pedro Pinto, Mons Erling Mathiesen, Amanda K. Jansen


Problem class, Node class, astar_search and best_first_graph_search from https://github.com/aimacode/aima-python/blob/master/search.py
"""

import math
import random
import sys
import copy
import os
from utils import (
    is_in, argmin, argmax, argmax_random_tie, probability, weighted_sampler,
    memoize, print_table, open_data, PriorityQueue, name,
    distance, vector_add
)

infinity = float('inf')


class ASARProblem(object):
    """The abstract class for a formal problem. You should subclass
    this and implement the methods actions and result, and possibly
    __init__, goal_test, and path_cost. Then you will create instances
    of your subclass and solve them with the various search functions."""


    def __init__(self, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal. Your subclass's constructor can add
        other arguments."""
        #self.airports, self.airplanes, self.aircraft_class, self.legs = self.load(filename)

        #Initial state: [[planeID, planepos, planeitme], profit, openlist of legs]

        self.goal = None
    def addtime(self, time1, time2):
        if time1 == '':
            time1 = None
        from datetime import datetime, timedelta
        try:
            T = int(time1[-6:-4])
        except:
            T = 0
        HM1 = datetime(year=1, month=1, day=1 + T, hour=int(time1[-4:-2]), minute=int(time1[-2:]))
        HM2 = timedelta(hours=int(time2[-4:-2]), minutes=int(time2[-2:]))
        DDadd = (HM1 + HM2)
        DHM = DDadd.strftime('%d%H%M')
        if DHM[-6:-4] == '01':
            res = DDadd.strftime('%H%M')
        else:
            res = DDadd.strftime('%d%H%M')
        return res
    def actions(self, state):
        moves = []
        for leg in state[2]:
            j = 2
            while j + 1 <= len(state[2][0]):
                moves.append([leg[0], leg[j]])
                j = j + 2
        moves2 = []
        for plane in self.airplanes:
            for m in moves:
                if plane[1] == m[1]:
                    for plane_status in state[0]:
                        if plane[0] == plane_status[0]:
                            if plane_status[1] == '':
                                moves2.append([m[0], plane[0]])
                            elif plane_status[1] == m[0][0]:
                                for airport in self.airports:
                                    if airport[0] == plane_status[1]:
                                        if int(airport[2]) > int(plane_status[2]) and int(airport[1]) <= int(plane_status[2]):
                                            for airport2 in self.airports:
                                                if m[0][1] == airport2[0]:
                                                    for leg2 in state[2]:
                                                        if m[0] == leg2[0]:
                                                            land_time = self.addtime(plane_status[2], leg2[1])
                                                            if int(airport2[2]) > int(land_time) and int(airport2[1]) <= int(land_time):
                                                                moves2.append([m[0], plane[0]])
        return moves2
    def result(self, state, action):
        L2=[]
        added_profit = 0
        model = []
        #cycle to determine the action starting time »ini_time«
        #and airplane model »model«
        for plane in state[0]:
               if plane[0] == action[1]:
                   if plane[2] == '': #if the plane hasnt been used
                       for airport in self.airports:
                           if action[0][0] == airport[0]:
                               ini_time = airport[1]   #starting time is set to departing airport opening time
                   else:
                       ini_time = plane[2] #else its the plane's time
                   for i in self.airplanes:
                      if plane[0] == i[0]:
                          model = i[1]
        #cycle to create the new list of not yet flown Legs »L2«
        #and travel time »T_time«
        #and use the airplane »model« to determine profit from current Leg »added_profit«
        for leg in state[2]:
            if leg[0] != action[0]:
                L2.append(leg)
            else:
                T_time=leg[1]
                for i in range(0,len(leg)):
                    if leg[i] == model:
                        added_profit = int(leg[i+1])
        #airplane rotation time »R_time« is determined from the »model«
        for i in self.aircraft_class:
            if i[0] == model:
                R_time = i[1]
        #new plane time of day »ITR« is calculated from »ini_time« , »T_time« and »R_time«
        IT = self.addtime(ini_time,T_time)
        ITR = self.addtime(IT,R_time)
        #new plane status is created
        #[plane_code, plane_location, plane_time]
        new_plane = []
        new_plane.append(action[1])
        new_plane.append(action[0][1])
        new_plane.append(ITR)
        new_planes = []
        #this new plane status added with the other planes unchanged status
        for i in state[0]:
            if i[0] == new_plane[0]:
                new_planes.append(tuple(new_plane))
            else:
                new_planes.append(tuple(i))
        #the new state is now assembled
        #[Planes_Status, Profit_So_far, Not_Yet_Flown_Legs, Schedule]
        new_planes = tuple(new_planes)
        L2 = tuple(L2)
        result_state = []
        result_state.append(new_planes)
        result_state.append(state[1]+added_profit)
        result_state.append(L2)
        SH = (*state[3], tuple([action[1],action[0],ini_time]))
        result_state.append(SH)
        result_state = tuple(result_state)
        return result_state
    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        Goal_test = True
        if not state[2]:  # test if state Legs yet to be flown is empty
            pass
        else:
            return False
        for leg in self.legs:  # test if all Legs in »L« are in the state schedule »s[-1]«
            m = 0
            for solution_leg in state[-1]:
                if leg[0] == solution_leg[1]:
                    m = m
                else:
                    m = m + 1
            if m == 0:
                return False
            else:
                pass
        for plane in state[0]:  # test if all the planes are in the same airport from where they started
            if plane[2] != '':
                for step in state[-1]:
                    if step[0] == plane[0]:
                        plane_start = step[1][0]
                        break
                #plane_start = next(i for i in state[3] if i[0] == plane[0])
                #plane_end = next(i for i in state[0] if i[0] == plane[0])
                if plane_start == plane[1]:
                    pass
                else:
                    return False
        return Goal_test
        # if isinstance(self.goal, list):
        #     return is_in(state, self.goal)
        # else:
        #     return state == self.goal
    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        #openlist = [[('LPPT', 'LPPR'), '0055', 'a320', 100, 'a330', 80],
         #           [('LPMA', 'LPPT'), '0145', 'a320', 90, 'a330', 120]] #modify to get openlist from state

        ac_class = ''
        for i in range(len(self.airplanes)):
            if action[1] == self.airplanes[i][0]:  # getting class of airplane used in action
                ac_class = self.airplanes[i][1]
        for leg in state1[2]:
            if leg[0] == action[0]:
                cost = 1 /int(leg[leg.index(ac_class) + 1])  # finding cost for class used in action
        if state1[1] == 0:
            path_cost = cost
        else:
            path_cost = 1 / state1[1] + cost
        #state2[1][0] = path_cost
        return path_cost
    def heuristic(self, node):
        """A best case estimation. Must be lower or equal to realistic minimum cost

            Evaluation function uses the heuristic. f(n) = g(n) + h(n). The heuristic, this funciton, is the h(n).
        """
        current_profit = int(node.state[1])
        if current_profit-self.max_profit == 0:
            heuristic = 0
        elif current_profit == 0:
            heuristic = 1
        else:
            heuristic = 1/current_profit - 1/self.max_profit
        return heuristic
    def load(self, file):  # loads a problem from a file object f
        self.airports ,self.aircraft_class, self.airplanes, self.legs = [], [], [], []

        for line in file:
            line = line.strip().split(' ')
            if line[0] == 'A':
                self.airports.append(tuple(line[1:]))
            elif line[0] == 'C':
                self.aircraft_class.append(tuple(line[1:]))
            elif line[0] == 'P':
                self.airplanes.append(tuple(line[1:]))
            elif line[0] == 'L':
                self.legs.append(tuple([(line[1], line[2])] + line[3:]))

        self.airports, self.aircraft_class, self.airplanes, self.legs = tuple(self.airports), tuple(self.aircraft_class), tuple(self.airplanes), tuple(self.legs)

        self.initial = tuple([tuple([tuple([plane[0], '', '']) for plane in self.airplanes]), 0, self.legs, tuple()])
        self.max_profit = 0
        for leg in self.legs:
            profit = int(leg[3])
            for profits in range(5, len(leg), 2):
                if int(leg[profits]) >= profit:
                    profit = int(leg[profits])
                self.max_profit += profit
        pass
    def solution(self, state):
        sol = [[sl[0]] + [sl[-1]] + [sl[-2]] for plane in self.airplanes for sl in state[-1] if plane[0] == sl[0]]
        sol2 = []
        for plane in self.airplanes:
            b = 0
            for i in sol:
                if plane[0] == i[0] and b == 0:
                    sol2.append([i[0]] + [i[1]] + [i[2]])
                    b = 1
                elif plane[0] == i[0] and b != 0:
                    for j in sol2:
                        if plane[0] == j[0]:
                            j.append(i[1])
                            j.append(i[2])
        return sol2
    def save(self, f, state): #saves a solution state s to a file object f
        if self.goal_test(state):
            sol = self.solution(state)
            for item in sol:
                f.write('S ')
                for element in item:
                    if type(element) == tuple:
                        f.write(element[0] + ' ')
                        f.write(element[1] + ' ')
                    else:
                        f.write(element + ' ')
                f.write('\n')
            f.write('P ' + str(state[1]))
        else:
            f.write('Infeasible')

        pass

# ______________________________________________________________________________


class Node:
    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node.  Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """[Figure 3.10]"""
        next_state = problem.result(self.state, action)
        next_node = Node(next_state, self, action,
                         problem.path_cost(self.path_cost, self.state,
                                           action, next_state))
        return next_node

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_graph_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)

def best_first_graph_search(problem, f):
    """Search the nodes with the lowest f scores first.
    You specify the function f(node) that you want to minimize; for example,
    if f is a heuristic estimate to the goal, then we have greedy best
    first search; if f is node.depth then we have breadth-first search.
    There is a subtlety: the line "f = memoize(f, 'f')" means that the f
    values will be cached on the nodes as they are computed. So after doing
    a best first search you can examine the f values of the path returned."""
    f = memoize(f, 'f')
    node = Node(problem.initial)
    frontier = PriorityQueue('min', f)
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                if f(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)
    return None
def astar_search(problem, h=None):
    """A* search is best-first graph search with f(n) = g(n)+h(n).
    You need to specify the h function when you call astar_search, or
    else in your Problem subclass."""
    h = memoize(h or problem.heuristic, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))

"""
A = [['LPPT', '0600', '2300'],
     ['LPPR', '0600', '2200'],
     ['LPFR', '0800', '2000'],
     ['LPMA', '0800', '2200']]

P = [['CS-TUA', 'a330'],
     ['CS-TTT', 'a320'],
     ['CS-TVA', 'a320']]

L = [[('LPPT', 'LPPR'), '0055', 'a320', 100, 'a330', 80],
     [('LPPR', 'LPPT'), '0055', 'a320', 100, 'a330', 80],
     [('LPPT', 'LPFR'), '0045', 'a320', 80, 'a330', 20],
     [('LPFR', 'LPPT'), '0045', 'a320', 80, 'a330', 20],
     [('LPPT', 'LPMA'), '0145', 'a320', 90, 'a330', 120],
     [('LPMA', 'LPPT'), '0145', 'a320', 90, 'a330', 120]]

C = [['a320', '0045'],
     ['a330', '0120']]
"""

problem = ASARProblem()
in_file = open('simple5.txt')
problem.load(in_file)
solution = astar_search(problem)
out_file = open('output.txt', 'w')
problem.save(out_file, solution.state)
out_file.close()
