import numpy as np
import itertools

# np.random.seed(1)


def weighted_selection(categories, probabilities):
    cat_list =[]
    prob_list = []
    chosen = 69
    for i in range(len(categories)):
        category = categories[i]
        if len(category) >= 1:
            cat_list.append(i)
            prob_list.append(probabilities[i])
    prob_list = np.array(prob_list)
    total_probability = np.sum(prob_list)
    random_number = np.random.uniform(0,total_probability)
    cumulative_prob = 0


    for i in range(len(prob_list)):
        probability = prob_list[i]
        cumulative_prob +=probability
        if random_number <= cumulative_prob:
            chosen = cat_list[i]

    chosen_category = categories[chosen]
    random_station = np.random.randint(0,len(chosen_category))
    station = chosen_category[random_station]


    return station


def location_hider(Info, ticket, seekers):
    """
    Compiles a list of all possible locations that the player can be on. These are split into 3 categories and a
    weighted selection is performed to determine one station where the player can be.
    :param Info: list of all stations and their connections
    :param ticket: Ticket used by player in previous round
    :param seekers: List of seekers
    :return: Possible location of Player
    """
    loc_seekers = []
    cat_1 = []  # Only taxis
    cat_2 = []  # bus + taxi
    cat_3 = []  # underground + taxi + bus
    for i in range(len(seekers)):
        loc_seekers.append(seekers[i].position)
    for i in range(len(Info)):
        station = Info[i][0]
        bus_con = Info[i][2]
        underground_con = Info[i][3]
        taxi_con = Info[i][4]
        check = False
        if station not in loc_seekers:
            for j in range(len(Info)):
                target = Info[j][0]
                bus_con_target = Info[j][2]
                underground_con_target = Info[j][3]
                if (bus_con_target != [0]) and (underground_con_target == [0]):
                    possible_locations = cat_2
                elif underground_con_target != [0]:
                    possible_locations = cat_3
                else:
                    possible_locations = cat_1
                if (target in bus_con and ticket == 0) or (target in underground_con and ticket == 1) or (
                        target in taxi_con and ticket == 2):
                    check = True
                if check and target not in possible_locations and target not in loc_seekers:
                    possible_locations.append(target)
    categories = [cat_1,cat_2,cat_3]
    probabilites = [0.3,0.3,0.4]
    location = weighted_selection(categories=categories, probabilities=probabilites)

    return location


def Arrange_seekers(seeker_list, player):
    """
    Creates a list of locations for the seekers to move to during the reveal round. The locations are those that are furthest from each seeker
    :param seeker_list: list of seekers
    :param player: Player entity
    :return: list containing the list of locations to move to
    """
    probabilities = [0.3,0.3,0.4]
    seeker_positions = []
    for seeker in seeker_list:
        seeker_positions.append(seeker.position)

    target_locations = []
    categories = [[],[],[]]
    all_moves = player.generate_nodes(station_list=[player.position]) # get all possible accesible station from current position
    station_list = []
    for move in all_moves:
        station = move[1]
        if station not in station_list:
            station_list.append(station)

    for station in station_list: # Rank them based on the category
        station_info = player.get_station_info(station=station)
        for i in range(3):
            if station_info[i+2] !=[0]:
                categories[i].append(station)

     # If you have more connections than seekers
    if len(station_list) > len(seeker_list):
        for i in range(len(seeker_list)):
            to_add = weighted_selection(categories=categories, probabilities=probabilities)
            target_locations.append(to_add)
            for category in categories:
                if to_add in category:
                    category.remove(to_add)

    # If you have fewer connections than seekers
    elif len(station_list) < len(seeker_list):
        for i in range(len(station_list)):
            target_locations.append(station_list[i])
        difference = abs(len(all_moves) - len(seeker_list))
        for i in range(difference):
            to_add = weighted_selection(categories=categories, probabilities=probabilities)
            target_locations.append(to_add)
    else:
        for i in range(len(station_list)):
            target_locations.append(station_list[i])



    difference_combinations = []
    for i in range(len(seeker_positions)):
        position = seeker_positions[i]
        buffer = []
        seeker = seeker_list[i]
        for location in target_locations:
            if seeker.minimise_distance(destination=location, node_list=None)[0] != 0:
                buffer.append(player.get_distance_difference(station_1=position, station_2=location))
            else:
                buffer.append(1000000)
        difference_combinations.append(buffer)
    difference_combinations = np.array(difference_combinations)
    best_score = 1E24
    best_combination = None
    combos = itertools.permutations(range(len(target_locations)), len(seeker_list))

    ## Use itertools to find the best combination that reduces the overall distance
    for combo in combos:
        if len(set(combo)) == len(seeker_list):
            score = sum(difference_combinations[i][combo[i]] for i in range(len(seeker_list)))
            if score < best_score:
                best_score = score
                best_combination = combo
    chosen_targets = []
    for i in range(len(seeker_list)):
        chosen_targets.append(target_locations[best_combination[i]])
    # chosen_targets = [target_locations[best_combination[0]], target_locations[best_combination[1]],
    #                   target_locations[best_combination[2]]]
    print(chosen_targets)
    return chosen_targets


def randomise_start_locations(Info, number_seekers):
    start_index = np.random.randint(0, len(Info), number_seekers + 1)
    while (len(set(start_index))) != len(start_index):
        start_index = np.random.randint(0, len(Info), number_seekers + 1)
    start_locations = []
    for i in range(number_seekers + 1):
        start_locations.append(Info[start_index[i]][0])
    # start_locations = [Info[start_index[0]][0],Info[start_index[1]][0], Info[start_index[2]][0], Info[start_index[3]][0] ]
    return start_locations



