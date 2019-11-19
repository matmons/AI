"""
Artificial Intelligence and Decision Systems
Pedro Pinto, Mons Erling Mathiesen, Amanda K. Jansen


Problem class, Node class, astar_search and best_first_graph_search from https://github.com/aimacode/aima-python/blob/master/search.py
"""

import math
import random
import sys
import copy
from utils import (
    is_in, argmin, argmax, argmax_random_tie, probability, weighted_sampler,
    memoize, print_table, open_data, PriorityQueue, name,
    distance, vector_add
)


class ASARProblem(object):
    """The abstract class for a formal problem. You should subclass
    this and implement the methods actions and result, and possibly
    __init__, goal_test, and path_cost. Then you will create instances
    of your subclass and solve them with the various search functions."""


    def __init__(self, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal. Your subclass's constructor can add
        other arguments."""
        # infile = open(filename, 'r')
        #
        # self.airports, self.airplanes, self.aircraft_class, self.legs = self.load(infile)
        # self.max_profit = 0
        # for leg in self.legs:
        #     profit = int(leg[3])
        #     for profits in range(5, len(leg), 2):
        #         if int(leg[profits]) >= profit:
        #             profit = int(leg[profits])
        #
        #         self.max_profit += profit
        # #Initial state: [[planeID, planepos, planeitme], profit, openlist of legs, solution]
        # self.initial = [[[plane[0], None, 0] for plane in self.airplanes], [0], [[list(leg[0])[0] + ' ' + list(leg[0])[1]] + leg[1:] for leg in self.legs]]
        # self.goal = None
        # self.outfile = open(outputfile, 'w')

    def addtime(self, time1, time2):
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
                            if plane_status[1] == None:
                                moves2.append([m[0], plane[0]])
                            elif plane_status[1] == m[0][0:4]:
                                for airport in self.airports:
                                    if airport[0] == plane_status[1]:
                                        if int(airport[2]) > int(plane_status[2]):
                                            for airport2 in self.airports:
                                                if m[0][5:9] == airport2[0]:
                                                    for leg2 in state[2]:
                                                        if m[0] == leg2[0]:
                                                            land_time = self.addtime(plane_status[2], leg2[1])
                                                            if int(airport2[2]) > int(land_time):
                                                                moves2.append([m[0], plane[0]])
        return moves2

    def results(self, state, action):
        import copy
        L2 = []
        added_profit = 0
        model = []
        # cycle to determine the action starting time »ini_time«
        # and airplane model »model«
        for plane in state[0]:
            if plane[0] == action[1]:
                if plane[2] == None:  # if the plane hasnt been used
                    for airport in self.airports:
                        if action[0][0:4] == airport[0]:
                            ini_time = airport[1]  # starting time is set to departing airport opening time
                else:
                    ini_time = plane[2]  # else its the plane'state time
                for i in self.airplanes:
                    if plane[0] == i[0]:
                        model = copy.deepcopy(i[1])
        # cycle to create the new list of not yet flown Legs »L2«
        # and travel time »T_time«
        # and use the airplane »model« to determine profit from current Leg »added_profit«
        for leg in state[2]:
            if leg[0] != action[0]:
                L2.append(leg)
            else:
                T_time = copy.deepcopy(leg[1])
                for i in range(0, len(leg)):
                    if leg[i] == model:
                        added_profit = int(leg[i + 1])
        # airplane rotation time »R_time« is determined from the »model«
        for i in self.aircraft_class:
            if i[0] == model:
                R_time = copy.deepcopy(i[1])
        # new plane time of day »ITR« is calculated from »ini_time« , »T_time« and »R_time«
        IT = self.addtime(ini_time, T_time)
        ITR = self.addtime(IT, R_time)
        # new plane status is created
        # [plane_code, plane_location, plane_time]
        new_plane = []
        new_plane.append(action[1])
        new_plane.append(action[0][5:9])
        new_plane.append(ITR)
        new_planeS = []
        # this new plane status added with the other planes unchanged status
        for plane in state[0]:
            if plane[0] == new_plane[0]:
                new_planeS.append(new_plane)
            else:
                new_planeS.append(plane)
        # the new state is now assembled
        # [Planes_Status, Profit_So_far, Not_Yet_Flown_Legs, Schedule]
        result_state = []
        result_state.append(new_planeS)
        result_state.append([state[1][0] + added_profit])
        result_state.append(L2)
        SH = copy.deepcopy(state[3])
        SH.append([action[1], action[0], ini_time])
        result_state.append(SH)
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
        for l in [[list(i[0])[0] + ' ' + list(i[0])[1]] + i[1:] for i in L]:  # test if all Legs in »L« are in the state schedule »s[-1]«
            m = 0
            for cl in state[-1]:
                if l[0] not in cl[1]:
                    m = m
                else:
                    m = m + 1
            if m == 0:
                return False
            else:
                pass
        for plane in state[0]:  # test if all the planes are in the same airport from where they started
            if plane[1] != None:
                Plane_Start = next(i for i in state[-1] if i[0] == plane[0])
                Plane_End = next(i for i in state[0] if i[0] == plane[0])
                if Plane_Start[1][0:4] == Plane_End[1]:
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
        openlist = [['LPPT LPPR', '0055', 'a320', 100, 'a330', 80],
                    ['LPMA LPPT', '0145', 'a320', 90, 'a330', 120]] #modify to get openlist from state
        action = ['LPPT LPPR', 'CS-TUA']
        ac_class = ''
        for i in range(len(self.airplanes)):
            if action[1] == self.airplanes[i][0]: #getting class of airplane used in action
                ac_class = self.airplanes[i][1]
        for leg in openlist:
            if leg[0] == action[0]:
                cost = 1/leg[leg.index(ac_class)+1] #finding cost for class used in action
        if state1[1][0] == 0:
            path_cost = cost
        else:
            path_cost = 1/state1[1][0] + cost
        #state2[1][0] = path_cost
        return path_cost



    def heuristic(self, node):
        """A best case estimation. Must be lower or equal to realistic minimum cost

            Evaluation function uses the heuristic. f(n) = g(n) + h(n). The heuristic, this funciton, is the h(n).
        """
        current_profit = int(node.state[1][0])
        if node.state[1][0] == 0:
            heuristic = 1 - 1/self.max_profit
        else:
            heuristic = 1/current_profit - 1/self.max_profit
        return heuristic

    def load(self, file):  # loads a problem from a file object f
        self.airports = set()
        self.aircraft_class = set()
        self.airplanes = set()
        self.legs = set()

        for line in file:
            line = line.strip().split(' ')
            if line[0] == 'A':
                self.airports.add(line[1:])
            elif line[0] == 'C':
                self.aircraft_class.add(line[1:])
            elif line[0] == 'P':
                self.airplanes.add(line[1:])
            elif line[0] == 'L':
                self.legs.add([(line[1], line[2])] + line[3:])
        self.initial = [[[plane[0], None, 0] for plane in self.airplanes], [0], [[list(leg[0])[0] + ' ' + list(leg[0])[1]] + leg[1:] for leg in self.legs]]
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
                    sol2.append([i[0]] + [i[-2]] + [i[-1]])
                    b = 1
                elif plane[0] == i[0] and b != 0:
                    for j in sol2:
                        if plane[0] == j[0]:
                            j.append(i[-2])
                            j.append(i[-1])
        return sol2
    def save(self, f, state): #saves a solution state s to a file object f
        R = []
        sol = self.solution(state)
        for item in sol[-1]:
            f.write('S ')
            for i in item:
                R.append(i)
                f.write('%state ' % i)
            f.write('\n')
        f.write('P'+sol[2])

        return

problem = ASARProblem()
file_in = open('example.txt','r')
problem.load(file_in)
file_in.close()
test_state1 = [[[plane[0], None, None] for plane in problem.airplanes], [0], [[list(leg[0])[0] + ' ' + list(leg[0])[1]] + leg[1:] for leg in problem.legs], []]
test_state2 = [[[plane[0], None, None] for plane in problem.airplanes], [0], [[list(leg[0])[0] + ' ' + list(leg[0])[1]] + leg[1:] for leg in problem.legs], []]
print('Airports: ',  problem.airports)
print(type(problem.airports))
# print('Aircraft class: ', problem.aircraft_class)
# print('Airplanes: ', problem.airplanes)
# print('Legs: ', problem.legs)
# actions = problem.actions(test_state1)
# results = problem.results(test_state1, actions[0])
# path_cost = problem.path_cost(0, test_state1, actions[0], test_state2)
# heuristic = problem.heuristic(test_state1)
# print(actions)
# print(results)
# print(problem.max_profit)
# print(heuristic)
# print(path_cost)
