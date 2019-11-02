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

L = [[ 'LPPT LPPR', '0055', 'a320', 100, 'a330', 80 ],
     [ 'LPPR LPPT', '0055', 'a320', 100, 'a330', 80 ],
     [ 'LPPT LPFR', '0045', 'a320', 80, 'a330', 20 ],
     [ 'LPFR LPPT', '0045', 'a320', 80, 'a330', 20 ],
     [ 'LPPT LPMA', '0145', 'a320', 90, 'a330', 120 ],
     [ 'LPMA LPPT', '0145', 'a320', 90, 'a330', 120 ]]
    
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


#  initial state creation   
# [[plane_name, plane_location, plane_time],[profit_so_far],[leg_to_fly1, leg_to_fly2],[schedule]]
ini_state = [[[x[0], None , None] for x in P],[0],L,[]]

# funtion that adds times from strings in the format 'HHMM'
# can be modified to include days, since at present it goes to '0000' after '2359'

def addtime(time1,time2):
    import datetime as dt
    HM1 = dt.time(int(time1[0:2]), int(time1[2:4]))
    HM2 = dt.timedelta(hours = int(time2[0:2]),minutes = int(time2[2:4]))
    HMadd = (dt.datetime.combine(dt.date(1,1,1),HM1) + HM2).time()
    HM = HMadd.strftime('%H%M')
    return HM

# actions function
# update1 so it only lets planes fly legs that start from their location
# update2 so it doesnt let planes takeoff or land after those airports close
# additional changes are needed to detect day changes in addtime function!!!
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


# results function

def results(s, a):
    
    import datetime as dt
    import copy
    
    L2=[]
    added_profit = 0
    model = []
    for g in s[0]:
           if g[0] == a[1]:
               if g[2] == None:
                   for e in A:
                       if a[0][0:4] == e[0]:
                           ini_time = e[1]     
               else:
                   ini_time = g[2]
               for i in P:
                  if g[0] == i[0]:
                      model = copy.deepcopy(i[1])
    for f in s[2]:
        if f[0] != a[0]:
            L2.append(f)
        else:
            T_time=copy.deepcopy(f[1])
            for i in range(0,len(f)):
                if f[i] == model: 
                    added_profit = f[i+1]
    for i in C:
        if i[0] == model:
            R_time =copy.deepcopy(i[1])
    e = int(ini_time[0:2])
    f = int(ini_time[2:4])                 
    d = int(T_time[0:2])
    b = int(T_time[2:4])
    c = int(R_time[0:2])
    g = int(R_time[2:4])
    result_state = []
    HH = dt.time(e, f)
    LH = dt.timedelta(hours = d,minutes = b)
    CH = dt.timedelta(hours = c,minutes = g)
    DH = (LH + CH)
    H = (dt.datetime.combine(dt.date(1,1,1),HH) + DH).time()
    new_plane = []
    new_plane.append(a[1])
    new_plane.append(a[0][5:9])
    new_plane.append(H.strftime('%H%M'))
    new_planeS = []
    for i in s[0]:
        if i[0] == new_plane[0]:
            new_planeS.append(new_plane)
        else:
            new_planeS.append(i)
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
    L1 = actions(ST) 
    move = L1[0]
    new_S = results(ST,move)
    ST = copy.deepcopy(new_S)

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
