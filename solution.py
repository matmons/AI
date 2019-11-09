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
        new_planeS = []
        #this new plane status added with the other planes unchanged status
        for i in state[0]:
            if i[0] == new_plane[0]:
                new_planeS.append(tuple(new_plane))
            else:
                new_planeS.append(tuple(i))
        #the new state is now assembled
        #[Planes_Status, Profit_So_far, Not_Yet_Flown_Legs, Schedule]
        new_planeS = tuple(new_planeS)
        L2 = tuple(L2)
        result_state = []
        result_state.append(new_planeS)
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
            if plane[1] != '':
                for step in state[-1]:
                    if step[0] == plane[0]:
                        plane_start = step[1][0]
                        break
                # plane_start = next(i for i in state[3] if i[0] == plane[0])
                # plane_end = next(i for i in state[0] if i[0] == plane[0])
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
