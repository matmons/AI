def validate_pos(state, actions): #returns a list of positional valid actions
    pos_valid_actions = actions[2:]
    current_pos = state[0][1]
    return pos_valid_actions
def validate_time(state, actions):
    time_valid_actions = []
    for action in actions:
        for plane in state[0]:
            if action[1] == plane[0]: #matching plane to plane used in action
                for airport in A: #self.airports
                    if action[0][0] == airport[0]: # match airport to 'From'
                        departure_times = airport[1:] # time limits departure
                    if action[0][1] == airport[0]: # match airport to 'To'
                        arrival_times = airport[1:] # time limits arrival
                if plane[2] is None:
                    plane[2] = departure_times[0]
                    land_time = addtime(plane[2], action[2])
                    print(land_time)
                else:
                    land_time = addtime(plane[2], action[2])
                #Checks if the plane has been used and if its departure time and arrival time are within the opening hours of airport the respective airports
                if (plane[2] is None) or ((plane[2] >= departure_times[0] and plane[2] <= departure_times[1]) and (land_time >= arrival_times[0] and land_time <= arrival_times[1])):
                    time_valid_actions.append(action)
    return time_valid_actions

def actions_mons(state):
    leg_duration_class = []
    for leg in state[2]: # state[2] = openlist
        class_index = 2
        while class_index+1 <= len(state[2][0]): #combines from-to with possible classes to fly the leg with
            leg_duration_class.append( [leg[0], leg[class_index], leg[1]]) #adds an action with the format: [('From', 'To'), 'aircraft_class']
            class_index += 2 #index of next class
    all_actions = []
    for action in leg_duration_class:
        for plane in P:
            if plane[1] == action[1]:
                all_actions.append([action[0], plane[0], action[2]]) #actions with the format: [('From', 'To'), 'airplane_id']
    #pos_valid_actions = validate_pos(state, all_actions) #removes positional invalid actions from all_actions
    valid_actions = validate_time(state, all_actions) #removes timely invalid actions from pos_valid_actions
    print(len(all_actions))
    print(len(valid_actions))
    return valid_actions