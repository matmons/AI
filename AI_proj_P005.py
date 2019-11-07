# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 23:59:52 2019

@author: Pedro
"""
import copy
# code assumes the input file was loaded
# and this was the result
class testclass(object):
    
    def __init__(self):

        self.airports = [[ 'LPPT' , '0600' , '2300'],
             [ 'LPPR' , '0600' , '2200'],
             [ 'LPFR' , '0800' , '2000' ],
             [ 'LPMA' , '0800' , '2200' ]]
        
        
        self.airplanes =[[ 'CS-TUA', 'a330' ],
            [ 'CS-TTT', 'a320' ],
            [ 'CS-TVA', 'a320' ]]
        
        self.legs = [[ ('LPPT','LPPR'), '0055', 'a320', 100, 'a330', 80 ],
             [ ('LPPR','LPPT'), '0055', 'a320', 100, 'a330', 80 ],
             [ ('LPPT','LPFR'), '0045', 'a320', 80, 'a330', 20 ],
             [ ('LPFR','LPPT'), '0045', 'a320', 80, 'a330', 20 ],
             [ ('LPPT','LPMA'), '0145', 'a320', 90, 'a330', 120 ],
             [ ('LPMA','LPPT'), '0145', 'a320', 90, 'a330', 120 ]]
            
        self.aircraft_class = [[ 'a320', '0045' ],
            [ 'a330', '0120' ]]
    
        
        # max profit cycle
        max_profit=0
        for leg in [[list(leg[0])[0]+' '+list(leg[0])[1]]+leg[1:] for leg in self.legs]:
            profit = leg[3]
            for j in range(3,len(leg),2):
                if leg[j] >= profit:
                    profit = leg[j]
            
            max_profit=max_profit+profit
        
        #List Comprehension to conver self.legs to our format 
        # that as been swaped out in every occurrences of self.legs for all functions
        # enabling them all to work with the standard self.legs
        self.myL = [[list(leg[0])[0]+' '+list(leg[0])[1]]+leg[1:] for leg in self.legs]
        
        #State structure   
        # [[plane_name, plane_location, plane_time],[profit_so_far],[legs_to_fly],[schedule]]
        # example : [[['CS-TUA', 'LPPR', '0715'], ['CS-TTT', None, None], ['CS-TVA', None, None]], 
        #              [80], 
        #              [[ 'LPPT LPPR', '0055', 'a320', 100, 'a330', 80 ], [ 'LPPR LPPT', '0055', 'a320', 100, 'a330', 80 ], [ 'LPPT LPFR', '0045', 'a320', 80, 'a330', 20 ], [ 'LPFR LPPT', '0045', 'a320', 80, 'a330', 20 ], [ 'LPPT LPMA', '0145', 'a320', 90, 'a330', 120 ], [ 'LPMA LPPT', '0145', 'a320', 90, 'a330', 120 ]],
        #              [['CS-TUA', 'LPPT LPPR', '0600']]]
        #[schedule] = [plane_name, Leg_flown, departure_time]
        
        #  initial state creation 
        self.ini_state = [[[x[0], None , None] for x in self.airplanes],[0],[[list(leg[0])[0]+' '+list(leg[0])[1]]+leg[1:] for leg in self.legs],[]]
    
    # funtion that adds times from strings in the format 
    # 'HHMM'+'HHMM' or 'ddHHMM'+'HHMM' then the output will be 
    # 'HHMM' or 'ddHHMM'+1day if it goes into day 2
    # exemple: '2200' + '0100' = '2300'
    #          '2200' + '0500' = '020300'
    def addtime(time1,time2):
        from datetime import datetime,timedelta
        try:
            T=int(time1[-6:-4])
        except:
            T=0  
        HM1 = datetime(year=1, month=1, day=1+T, hour=int(time1[-4:-2]), minute= int(time1[-2:]))
        HM2 = timedelta(hours=int(time2[-4:-2]),minutes=int(time2[-2:]))
        DDadd = (HM1 + HM2)
        DHM = DDadd.strftime('%d%H%M')
        if DHM[-6:-4] == '01':
            res = DDadd.strftime('%H%M')
        else:
            res = DDadd.strftime('%d%H%M')
        return res
         
    # actions function
    # update1 so it only lets planes fly legs that start from their location
    # update2 so it doesnt let planes takeoff or land after those airports close
    # update3 with the new version of addtime it should detect day changes
    def actions(self,state):
        moves = []
        for leg in state[2] :
            j=2
            while j+1 <= len(state[2][0]):
                moves.append( [leg[0],leg[j]] )
                j=j+2
        moves2 = []
        for plane in self.airplanes:
            for m in moves:
                if plane[1] == m[1]:
                    for plane_status in state[0]:
                        if plane[0] == plane_status[0]:
                            if plane_status[1] == None:
                                moves2.append([m[0],plane[0]])
                            elif plane_status[1] == m[0][0:4]:
                                for airport in self.airports:
                                    if airport[0] == plane_status[1]:
                                        if int(airport[2]) > int(plane_status[2]):
                                            for airport2 in self.airports:
                                                if m[0][5:9] == airport2[0]:
                                                    for leg2 in state[2]:
                                                        if m[0] == leg2[0]:
                                                            land_time = self.addtime(plane_status[2],leg2[1])
                                                            if int(airport2[2]) > int(land_time):
                                                                moves2.append([m[0],plane[0]])
        return moves2
    
    # results function
    # update1 changed to make use of function addtime
    def results(self, state, action):
        import copy
        L2=[]
        added_profit = 0
        model = []
        #cycle to determine the action starting time »ini_time«
        #and airplane model »model«
        for plane in state[0]:
               if plane[0] == action[1]:
                   if plane[2] == None: #if the plane hasnt been used 
                       for airport in self.airports:
                           if action[0][0:4] == airport[0]:
                               ini_time = airport[1]   #starting time is set to departing airport opening time    
                   else:
                       ini_time = plane[2] #else its the plane'state time
                   for i in self.airplanes:
                      if plane[0] == i[0]:
                          model = copy.deepcopy(i[1])
        #cycle to create the new list of not yet flown Legs »L2« 
        #and travel time »T_time«
        #and use the airplane »model« to determine profit from current Leg »added_profit«
        for leg in state[2]:
            if leg[0] != action[0]:
                L2.append(leg)
            else:
                T_time=copy.deepcopy(leg[1])
                for i in range(0,len(leg)):
                    if leg[i] == model: 
                        added_profit = leg[i+1]
        #airplane rotation time »R_time« is determined from the »model«
        for i in self.aircraft_class:
            if i[0] == model:
                R_time =copy.deepcopy(i[1])
        #new plane time of day »ITR« is calculated from »ini_time« , »T_time« and »R_time« 
        IT = self.addtime(ini_time,T_time)
        ITR = self.addtime(IT,R_time)
        #new plane status is created
        #[plane_code, plane_location, plane_time]
        new_plane = []
        new_plane.append(action[1])
        new_plane.append(action[0][5:9])
        new_plane.append(ITR)
        new_planeS = []
        #this new plane status added with the other planes unchanged status
        for plane in state[0]:
            if plane[0] == new_plane[0]:
                new_planeS.append(new_plane)
            else:
                new_planeS.append(plane)
        #the new state is now assembled
        #[Planes_Status, Profit_So_far, Not_Yet_Flown_Legs, Schedule]
        result_state = []
        result_state.append(new_planeS)
        result_state.append([state[1][0]+added_profit])
        result_state.append(L2)
        SH =copy.deepcopy(state[3])
        SH.append([action[1],action[0],ini_time])
        result_state.append(SH)  
        return result_state
    
    # small function test cycle
    
    ST = copy.deepcopy(self.ini_state)
    for leg in [[list(leg[0])[0]+' '+list(leg[0])[1]]+leg[1:] for leg in self.legs]:   
        L1 = actions(ST) 
        move = L1[0]
        new_S = results(ST,move)
        ST = copy.deepcopy(new_S)
    
    #goal_test function
        
    def goal_test(state):
        Goal_test = 0
        if not state[2]: #test if state Legs yet to be flown is empty
            Goal_test = Goal_test
        else:
            Goal_test = Goal_test+1
        for l in [[list(leg[0])[0]+' '+list(leg[0])[1]]+leg[1:] for leg in self.legs]: #test if all Legs in »self.legs« are in the state schedule »state[-1]«
            m=0
            for cl in state[-1]:
                if l[0] not in cl[1]:
                    m =m 
                else:
                    m =m+1
            if m == 0:
                Goal_test = Goal_test+1
            else:
                Goal_test = Goal_test
        for plane_status in state[0]: #test if all the planes are in the same airport from where they started
            if plane_status[1] != None:
                Plane_Start = next(i for i in state[-1] if i[0] == plane_status[0])
                Plane_End = next(i for i in state[0] if i[0] == plane_status[0])
                if Plane_Start[1][0:4] == Plane_End[1]:
                    Goal_test=Goal_test
                else:
                    Goal_test=Goal_test+1
                    
        if Goal_test == 0:
            Goal = True
        else:
            Goal = False
        return Goal
    
    Gtest1 = goal_test(ST)           
    #print(Gtest1)
    
    Gtest2 = goal_test(self.ini_state)           
    #print(Gtest2)
    
    test_state = [[['CS-TUA', 'LPPR', '0715'], ['CS-TTT', None, None], ['CS-TVA', None, None]], [80], [[list(leg[0])[0]+' '+list(leg[0])[1]]+leg[1:] for leg in self.legs][1:], [['CS-TUA', 'LPPT LPPR', '0600']]]
    
    Act = actions(test_state)
    
    Gtest3 = goal_test(test_state)           
    #print(Gtest3)
    #
    
    
    #['CS-TUA', 'LPPT LPPR', '0600']
    #['CS-TTT','CS-TVA'] 
    ST2 =ST[-1]+[['CS-TTT', 'LPPR LPPM', '0600']]+[['CS-TTT', 'LPPM LPPT', '0800']]+[['CS-TTT', 'LPPT LPPR', '1000']]+[['CS-TVA', 'LPFR LPMA', '0700']]+[['CS-TVA', 'LPMA LPPM', '0900']]+[['CS-TVA', 'LPPM LPFR', '1100']]
    #
    #sul = [[sl[0]]+[sl[-1]]+[sl[-2]] for plane in self.airplanes for sl in ST[-1] if plane[0]==sl[0]]
    #sul2 = [sul[0]]
    #print(sul[1][0])
    #print(sul2[0])
    #for j in range(1,len(sul)):
    #    for i in sul2:
    #        if sul[j][0] == i[0]:
    #            sul2[0].append(sul[j][-2])
    #            sul2[0].append(sul[j][-1])
    #print(sul2)
    #for plane in self.airplanes:
    #    for sl in ST2:
    #        if plane[0] == sl[0]:
    #            print(sl[0])
    #print(ST2[6][0])
    sul = [[sl[0]]+[sl[-1]]+[sl[-2]] for plane in self.airplanes for sl in ST2 if plane[0]==sl[0]]
    
    
    #sul3 = []
    #for plane in self.airplanes:
    #    for sl in ST2:
    #        if plane[0] == sl [0]:
    #            sul3.append([sl[0]]+[sl[-1]]+[sl[-2]])
                
    
    sul2 = []
    for plane in self.airplanes:
        b = 0
        for i in sul:
            if plane[0] == i[0] and b == 0:
                sul2.append([i[0]]+[i[-2]]+[i[-1]])
                b = 1
            elif plane[0] == i[0] and b != 0:
                for j in sul2:
                    if plane[0] == j[0]:
                        j.append(i[-2])
                        j.append(i[-1])
    
    def solution(state):
        sol = [[sl[0]]+[sl[-1]]+[sl[-2]] for plane in self.airplanes for sl in state[-1] if plane[0]==sl[0]]
        sol2 = []
        for plane in self.airplanes:
            b = 0
            for i in sol:
                if plane[0] == i[0] and b == 0:
                    sol2.append([i[0]]+[i[-2]]+[i[-1]])
                    b = 1
                elif plane[0] == i[0] and b != 0:
                    for j in sol2:
                        if plane[0] == j[0]:
                            j.append(i[-2])
                            j.append(i[-1])
        return sol2
        
    T_S1 = solution(ST)    
    ST3 = ST[:-1]+[ST2]       
    T_S2 = solution(ST3)       
    #print(sul2)
    
    #R=[]
    #open('save.txt', 'w') as f
    #
    #def save(state,f):
    #    for item in state[-1]:
    #        f.write('S ')
    #        for i in item:
    #            R.append(i)
    #            f.write('%state ' % i)
    #        f.write('\n')
    #    f.write('P'+state[2])
    #    return
    #    
    #
    
