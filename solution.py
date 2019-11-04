"""
Artificial Intelligence and Decision Systems
Pedro Pinto, Mons Erling Mathiesen, Amanda K. Jansen


Problem class, Node class, astar_search and best_first_graph_search from https://github.com/aimacode/aima-python/blob/master/search.py
"""

import math
import random
import sys
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


    def __init__(self, filename, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal. Your subclass's constructor can add
        other arguments."""
        self.airports, self.airplanes, self.aircraft_class, self.legs = self.load(filename)
        self.max_profit = 0
        for leg in self.legs:
            profit = int(leg[4])
            for profits in range(4, len(leg), 2):
                if int(leg[profits]) >= profit:
                    profit = int(leg[profits])
                self.max_profit += profit
        #Initial state: [[planeID, planepos, planeitme], profit, openlist of legs]
        self.initial = [[[plane[0], None, 0] for plane in self.airplanes], [0], self.legs]
        self.goal = None

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""

        raise NotImplementedError

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

        raise NotImplementedError

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        openlist = [['LPPT LPPR', '0055', 'a320', 100, 'a330', 80]] #modify to get openlist from state
        action = ['LPPT LPPR', 'CS-TUA'] #given
        ac_class = ''
        for i in range(len(self.airplanes)):
            if action[1] == self.airplanes[i][0]: #getting class of airplane used in action
                ac_class = self.airplanes[i][1]
        for leg in openlist:
            if leg[0] == action[0]:
                cost = 1/leg[leg.index(ac_class)+1] #finding cost for class used in action
        path_cost = c + cost
        return path_cost



    def heuristic(self, state):
        """A best case estimation. Must be lower or equal to realistic minimum cost

            Evaluation function uses the heuristic. f(n) = g(n) + h(n). The heuristic, this funciton, is the h(n).
        """
        current_profit = int(state[1][0])
        if current_profit-self.max_profit == 0:
            heuristic = 0
        else:
            heuristic = 1/current_profit - 1/self.max_profit
        return heuristic

    def load(self, file):  # loads a problem from a file object f
        airports = []
        aircraft_class = []
        airplanes = []
        legs = []

        for line in open(file, 'r'):
            line = line.strip().split(' ')
            if line[0] == 'A':
                airports.append(line[1:])
            elif line[0] == 'C':
                aircraft_class.append(line[1:])
            elif line[0] == 'P':
                airplanes.append(line[1:])
            elif line[0] == 'L':
                legs.append(line[1:])

        return airports, airplanes, aircraft_class, legs

    def save(f,s): #saves a solution state s to a file object f
        return 'Saved'






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
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))


A = [['LPPT', '0600', '2300'],
     ['LPPR', '0600', '2200'],
     ['LPFR', '0800', '2000'],
     ['LPMA', '0800', '2200']]

P = [['CS-TUA', 'a330'],
     ['CS-TTT', 'a320'],
     ['CS-TVA', 'a320']]

L = [['LPPT LPPR', '0055', 'a320', 100, 'a330', 80],
     ['LPPR LPPT', '0055', 'a320', 100, 'a330', 80],
     ['LPPT LPFR', '0045', 'a320', 80, 'a330', 20],
     ['LPFR LPPT', '0045', 'a320', 80, 'a330', 20],
     ['LPPT LPMA', '0145', 'a320', 90, 'a330', 120],
     ['LPMA LPPT', '0145', 'a320', 90, 'a330', 120]]

C = [['a320', '0045'],
     ['a330', '0120']]

problem = ASARProblem('example.txt')
test_state1 = [[[plane[0], None, 0] for plane in problem.airplanes], [200], problem.legs]
test_state2 = [[[plane[0], None, 0] for plane in problem.airplanes], [400], problem.legs]
action = ['LPPT LPPR', 'CS-TUA']
print('Airports: ',  problem.airports)
print('Aircraft class: ', problem.aircraft_class)
print('Airplanes: ', problem.airplanes)
print('Legs: ', problem.legs)
path_cost = problem.path_cost(3, test_state1, action, test_state2)
heuristic = problem.heuristic(test_state1)
print(heuristic)
print(path_cost)
