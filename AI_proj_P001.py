# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 14:53:06 2019

@author: Pedro
"""

# code assumes the input file was loaded
# and this was the result

import copy

A = [[ 'LPPT' , '0600' , '2300'],
     [ 'LPPR' , '0600' , '2200'],
     [ 'LPFR' , '0800' , '2000' ],
     [ 'LPMA' , '0800' , '2200' ]]


P =[[ 'CS-TUA', 'a330' ],
    [ 'CS-TTT', 'a320' ],
    [ 'CS-TVA', 'a320' ]]

L = [[ ('LPPT', 'LPPR'), '0055', 'a320', 100, 'a330', 80 ],
     [ ('LPPR', 'LPPT'), '0055', 'a320', 100, 'a330', 80 ],
     [ ('LPPT', 'LPFR'), '0045', 'a320', 80, 'a330', 20 ],
     [ ('LPFR', 'LPPT'), '0045', 'a320', 80, 'a330', 20 ],
     [ ('LPPT', 'LPMA'), '0145', 'a320', 90, 'a330', 120 ],
     [ ('LPMA', 'LPPT'), '0145', 'a320', 90, 'a330', 120 ]]
    
C = [[ 'a320', '0045' ],
    [ 'a330', '0120' ]]

# max profit cycle
max_profit=0
for leg in L:
    profit = leg[3]
    for profits in range(3,len(leg),2):
        if leg[profits] >= profit:
            profit = leg[profits]

    max_profit += profit
print(max_profit)


#State structure   
# [[plane_name, plane_location, plane_time],[profit_so_far],[legs_to_fly],[schedule]]
# example : [[['CS-TUA', 'LPPR', '0715'], ['CS-TTT', None, None], ['CS-TVA', None, None]], 
#              [80], 
#              [[ 'LPPT LPPR', '0055', 'a320', 100, 'a330', 80 ], [ 'LPPR LPPT', '0055', 'a320', 100, 'a330', 80 ], [ 'LPPT LPFR', '0045', 'a320', 80, 'a330', 20 ], [ 'LPFR LPPT', '0045', 'a320', 80, 'a330', 20 ], [ 'LPPT LPMA', '0145', 'a320', 90, 'a330', 120 ], [ 'LPMA LPPT', '0145', 'a320', 90, 'a330', 120 ]],
#              [['CS-TUA', 'LPPT LPPR', '0600']]]
#[schedule] = [plane_name, Leg_flown, departure_time]

#  initial state creation 
ini_state = [[[x[0], None , None] for x in P],[0],L,[]]


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
def actions(s):

    moves = []
    for i in s[2] :
        j=2
        while j+1 <= len(s[2][0]):
            moves.append( [i[0],i[j]] )
            j=j+2
    moves2 = []
    for p in P:
        for m in moves:
            if p[1] == m[1]:
                for sz in s[0]:
                    if p[0] == sz[0]:
                        if sz[1] == None:
                            moves2.append([m[0],p[0]])
                        elif sz[1] == m[0][0:4]:
                            for a in A:
                                if a[0] == sz[1]:
                                    if int(a[2]) > int(sz[2]):
                                        for al in A:
                                            if m[0][5:9] == al[0]:
                                                for st in s[2]:
                                                    if m[0] == st[0]:
                                                        land_time = addtime(sz[2],st[1])
                                                        if int(al[2]) > int(land_time):
                                                            moves2.append([m[0],p[0]])
    return moves2

def actions2(s):

    moves = []
    for i in s[2] :
        j=2
        while j+1 <= len(s[2][0]):
            moves.append( [list(i[0]),i[j]] )
            j=j+2
    moves2 = []
    for p in P:
        for m in moves:
            if p[1] == m[1]:
                for sz in s[0]:
                    if p[0] == sz[0]:
                        if sz[1] == None:
                            moves2.append([m[0],p[0]])
                        elif sz[1] == m[0][0:4]:
                            for a in A:
                                if a[0] == sz[1]:
                                    if int(a[2]) > int(sz[2]):
                                        for al in A:
                                            if m[0][5:9] == al[0]:
                                                for st in s[2]:
                                                    if m[0] == st[0]:
                                                        land_time = addtime(sz[2],st[1])
                                                        if int(al[2]) > int(land_time):
                                                            moves2.append([m[0],p[0]])
    return moves2


# results function
# update1 changed to make use of function addtime
def results(s, a):
    import copy
    L2=[]
    added_profit = 0
    model = []
    #cycle to determine the action starting time »ini_time«
    #and airplane model »model«
    for g in s[0]:
           if g[0] == a[1]:   
               if g[2] == None:  #if the plane hasnt been used 
                   for e in A:
                       if a[1] == e[0]:
                           ini_time = e[1]  #starting time is set to departing airport opening time   
               else:
                   ini_time = g[2] #else its the plane's time
               for i in P:
                  if g[0] == i[0]:
                      model = copy.deepcopy(i[1])
    #cycle to create the new list of not yet flown Legs »L2« 
    #and travel time »T_time«
    #and use the airplane »model« to determine profit from current Leg »added_profit«
    for f in s[2]:
        if f[0] != a[0]:
            L2.append(f)
        else:
            T_time=copy.deepcopy(f[1])
            for i in range(0,len(f)):
                if f[i] == model: 
                    added_profit = f[i+1]
    #airplane rotation time »R_time« is determined from the »model«
    for i in C:
        if i[0] == model:
            R_time =copy.deepcopy(i[1])
    #new plane time of day »ITR« is calculated from »ini_time« , »T_time« and »R_time«          
    IT = addtime(ini_time,T_time)
    ITR = addtime(IT,R_time)
    #new plane status is created
    #[plane_code, plane_location, plane_time]
    new_plane = []
    new_plane.append(a[1])
    new_plane.append(a[0][5:9])
    new_plane.append(ITR)
    new_planeS = []
    #this new plane status added with the other planes unchanged status
    for i in s[0]:
        if i[0] == new_plane[0]:
            new_planeS.append(new_plane)
        else:
            new_planeS.append(i)
    #the new state is now assembled
    #[Planes_Status, Profit_So_far, Not_Yet_Flown_Legs, Schedule]
    result_state = []
    result_state.append(new_planeS)
    result_state.append([s[1][0]+added_profit])
    result_state.append(L2)
    SH =copy.deepcopy(s[3])
    SH.append([a[1],a[0],ini_time])
    result_state.append(SH)  
    return result_state

# small function test cycle

ST = copy.deepcopy(ini_state)
for i in L:
    L1 = actions2(ST)
    print(L1)
    move = L1[0]
    new_S = results(ST,move)
    ST = copy.deepcopy(new_S)

#goal_test function
     
def goal_test(s):
    Goal_test = 0
    if not s[2]: #test if state Legs yet to be flown is empty
        Goal_test = Goal_test
    else:
        Goal_test = Goal_test+1
    for l in L: #test if all Legs in »L« are in the state schedule »s[-1]«
        m=0
        for cl in s[-1]:
            if l[0] not in cl[1]:
                m =m 
            else:
                m =m+1
        if m == 0:
            Goal_test = Goal_test+1
        else:
            Goal_test = Goal_test
    for p in s[0]: #test if all the planes are in the same airport from where they started
        if p[1] != None:
            Plane_Start = next(i for i in s[-1] if i[0] == p[0])
            Plane_End = next(i for i in s[0] if i[0] == p[0])
            if Plane_Start[1][0:4] == Plane_End[1]:
                Goal_test=Goal_test
            else:
                Goal_test=Goal_test+1
                
    if Goal_test == 0:
        Goal = True
    else:
        Goal = False
    return Goal
     
     
#  under construction solution function   
     
#def sol(s):
#    S=[[s[3][0][0],s[3][0][2],s[3][0][1]]]
#    for i in s[3]:
#        if i[0] == S[0][0]:
#            for j in range(2,len(S[0]),2):
#                if i[1] != S[j]:
#                    S.append(i[2])
#                    s.append(i[1])
#                    
#                    
#                
#    return S
#
#solv = sol(ST)

test_state = [[['CS-TUA', 'LPPR', '0715'], ['CS-TTT', None, None], ['CS-TVA', None, None]], [80], L[1:], [['CS-TUA', 'LPPT LPPR', '0600']]]
#
# moves3 =[]
# print(test_state[2][0][0])
# moves3.append(list(test_state[2][0][0]))
# print(moves3)
