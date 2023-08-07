import copy
import csv
from datetime import datetime

import numpy as np
import itertools

import pandas as pd

from data_read import loc_cat


# np.random.seed(1)


def weighted_selection(categories, probabilities):
    cat_list = []
    prob_list = []
    chosen = 69
    for i in range(len(categories)):
        category = categories[i]
        if len(category) >= 1:
            cat_list.append(i)
            prob_list.append(probabilities[i])
    prob_list = np.array(prob_list)
    total_probability = np.sum(prob_list)
    random_number = np.random.uniform(0, total_probability)
    cumulative_prob = 0

    for i in range(len(prob_list)):
        probability = prob_list[i]
        cumulative_prob += probability
        if random_number <= cumulative_prob:
            chosen = cat_list[i]
    try:
        chosen_category = categories[chosen]
        random_station = np.random.randint(0, len(chosen_category))
        station = chosen_category[random_station]
    except IndexError:
        print("Failure!!")
        print("chosen", chosen)
        print("categories", categories)
        print("prob list", prob_list)
        print(loc_cat[0][0] / loc_cat[0][1], loc_cat[1][0] / loc_cat[1][1], loc_cat[2][0] / loc_cat[2][1])
        station = categories[0][0]

    return station


def location_hider(player, possible_locations, loc_cat=loc_cat):
    """
    Compiles a list of all possible locations that the player can be on. These are split into 3 categories and a
    weighted selection is performed to determine one station where the player can be.
    :param Info: list of all stations and their connections
    :param ticket: Ticket used by player in previous round
    :param seekers: List of seekers
    :return: Possible location of Player
    """
    cat_1 = []  # Only taxis
    cat_2 = []  # bus + taxi
    cat_3 = []  # underground + taxi + bus
    for location in possible_locations:
        station_info = player.get_station_info(station=location)
        bus_con = station_info[2]
        underground_con = station_info[3]
        if underground_con != [0]:
            cat_3.append(location)
        elif bus_con != [0]:
            cat_2.append(location)
        else:
            cat_1.append(location)
    if len(cat_1) == 0 and len(cat_2) == 0 and len(cat_3) == 0:
        print(possible_locations)

    categories = [cat_1, cat_2, cat_3]
    probabilities = [loc_cat[0][0] / loc_cat[0][1], loc_cat[1][0] / loc_cat[1][1], loc_cat[2][0] / loc_cat[2][1]]
    location = weighted_selection(categories=categories, probabilities=probabilities)
    return location


def Arrange_seekers(seeker_list, player):
    """
    Creates a list of locations for the seekers to move to during the reveal round. The locations are those that are furthest from each seeker
    :param seeker_list: list of seekers
    :param player: Player entity
    :return: list containing the list of locations to move to
    """
    probabilities = [0.3, 0.3, 0.4]
    seeker_positions = []
    for seeker in seeker_list:
        seeker_positions.append(seeker.position)

    target_locations = []
    categories = [[], [], []]
    all_moves = player.generate_nodes(
        station_list=[player.position])  # get all possible accesible station from current position
    station_list = []
    for move in all_moves:
        station = move[1]
        if station not in station_list:
            station_list.append(station)

    for station in station_list:  # Rank them based on the category
        station_info = player.get_station_info(station=station)
        if station_info[4] != [0]:
            categories[2].append(station)
        elif station_info[3] != [0]:
            categories[1].append(station)
        else:
            categories[0].append(station)

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

    if best_combination is None:
        print(combos)
        print(target_locations)
        best_combination = list(combos)[0]
    chosen_targets = []
    print("best combo", best_combination)
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


def write_loc_cat_file(file_name, loc_cat=loc_cat):
    file = open(file_name, "w", newline="")
    data = [{"a": loc_cat[0][0], "n": loc_cat[0][1]},
            {"a": loc_cat[1][0], "n": loc_cat[1][1]},
            {"a": loc_cat[2][0], "n": loc_cat[2][1]}]
    header = ["a", "n"]
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()
    writer.writerows(data)

    return 0


def write_data_file(file_name, alpha_normal, gamma_normal, alpha_reveal, gamma_reveal, C, W, Caught, comments, Rounds,
                    coverage):
    file = open(file_name, "r")
    lines = file.readlines()
    read_data = pd.DataFrame(
        columns=["Date", "Caught", "Rounds", "C", "W", "Alpha_normal", "Gamma_normal", "Alpha_reveal", "Gamma_reveal",
                 "Coverage", "Comments"])
    for line in lines:
        line = line[:-1]
        columns = line.split(",")
        columns = columns[1:]

        if columns[0] != "Date":
            read_data.loc[len(read_data)] = columns
    file.close()
    date = datetime.now().strftime("%m/%d/%Y")
    data_to_add = [date, Caught, Rounds, C, W, alpha_normal, gamma_normal, alpha_reveal, gamma_reveal, coverage,
                   comments]
    read_data.loc[len(read_data)] = data_to_add
    read_data.to_csv(file_name)

    return 0


def write_q_file(file_name, Q_values):
    Q_Values_df = pd.DataFrame(columns=["origin", "destination", "transport", "value"])
    for entry in Q_values:
        Q_Values_df.loc[len(Q_Values_df)] = entry
    Q_Values_df.to_csv(file_name)
    return 0


def update_centralised_q_values(seekers, Q_values):
    individual_values = []
    for i in range(len(Q_values)):
        buffer = []
        for seeker in seekers:
            seeker_q = seeker.q_values
            buffer.append(seeker_q[i][3])
        individual_values.append(buffer)

    for i in range(len(individual_values)):
        average = np.average(individual_values[i])
        Q_values[i][3] = average
    return Q_values


def update_possible_location_list(possible_locations, Info, seekers, ticket):
    loc_seekers = []
    for seeker in seekers:
        loc_seekers.append(seeker.position)

    if possible_locations is None:
        ## Find every station reachable using the provided ticket ##
        possible_locations = []
        Info_list = Info
        for i in range(len(Info)):
            station = Info[i][0]
            bus_con = Info[i][2]
            underground_con = Info[i][3]
            taxi_con = Info[i][4]
            con = [bus_con, underground_con, taxi_con]
            check = False
            if station not in loc_seekers:
                for j in range(len(Info_list)):
                    target = Info_list[j][0]
                    if target in con[ticket]:
                        check = True
                    if check and target not in possible_locations and target not in loc_seekers:
                        possible_locations.append(target)
    else:
        new_list = []
        for i in range(0, len(possible_locations)):
            station = possible_locations[i]
            nodes = seekers[0].generate_nodes([station])
            for node in nodes:
                if node[1] not in new_list and node[2] == ticket and node[1] not in loc_seekers:
                    new_list.append(node[1])
        if len(new_list) > 0:
            possible_locations = new_list
        else:
            print("ERROR WITH POSSIBLE LOCATIONS")
            print("possible location", possible_locations)
            print("loc seekers", loc_seekers)

    for station in loc_seekers:
        if station in possible_locations:
            possible_locations.remove(station)
    return possible_locations


def Selection(seeker, nodes, leaf_nodes, C, W):
    selection_scores = []
    for node in leaf_nodes:
        if node != 0:
            v_i = seeker.UCT(parent=node[0], child=node[1], transport=node[2], C=C, W=W, Q_values=seeker.q_values,
                             Visits=seeker.visits)
            selection_scores.append(v_i)
        else:
            selection_scores.append(-69)
    chosen_leaf_node_index = np.argmax(np.array(selection_scores))
    chosen_node = leaf_nodes[chosen_leaf_node_index]
    chosen_node_index = 0
    for i in range(len(nodes)):
        node = nodes[i]
        if chosen_node == node:
            chosen_node_index = i
    return chosen_node_index, chosen_leaf_node_index, chosen_node


def Simulation(seekers, player, chosen_move, agent, possible_location, Round, Round_limit, coalition_reduction):
    Dummy_positions = []
    Dummies = []
    reward = 0
    for seeker in seekers:
        Dummies.append(copy.deepcopy(seeker))
        Dummy_positions.append(seeker.position)

    Player_sim = copy.deepcopy(player)
    Dummies = np.array(Dummies)
    Player_sim.tickets[chosen_move[2]] += 1

    for i in range(agent + 1, len(Dummies)):
        best_move, ticket_to_use = Dummies[i].minimise_distance(destination=possible_location,
                                                                exclude_stations=Dummy_positions, node_list=[])
        if best_move != 0:
            Dummies[i].move(destination=best_move, ticket=ticket_to_use)
            Dummy_positions[i] = best_move
            Player_sim.tickets[ticket_to_use] += 1

    sim_running = True
    for Dummy in Dummies:
        if Dummy.caught(Player_sim):
            sim_running = False

    while sim_running:
        # Player's move
        player_moves = []
        distances = []
        for Dummy in Dummies:
            max_distance_target, transport = Player_sim.maximise_distance(target=Dummy.position,
                                                                          seeker_locs=Dummy_positions)
            if max_distance_target != 0:
                player_moves.append([Player_sim.position, max_distance_target, transport])
                distances.append(
                    Player_sim.get_distance_difference(station_1=max_distance_target, station_2=Dummy.position))
        if len(player_moves) > 0:
            move_chosen = player_moves[np.argmax(np.array(distances))]
            Player_sim.move(destination=move_chosen[1], ticket=move_chosen[2])
            possible_location = Player_sim.position

        # Seekers' move
        for i in range(len(Dummies)):
            best_move, ticket_to_use = Dummies[i].minimise_distance(destination=possible_location,
                                                                    exclude_stations=Dummy_positions, node_list=[])
            if best_move != 0:
                Dummies[i].move(destination=best_move, ticket=ticket_to_use)
                Dummy_positions[i] = best_move
                Player_sim.tickets[ticket_to_use] += 1

            if Dummies[i].caught(Player_sim):
                sim_running = False
                if i == agent:
                    reward = 1
                else:
                    reward = 1 - coalition_reduction

        Round += 1
        if Round > Round_limit:
            sim_running = False

    return reward


def MCTS(seekers, player, Round, Round_limit, possible_location, N, C, W, r, alpha, gamma):
    ## Initialise ##
    counter = 0
    agent = 0
    nodes = [[]]
    leaf_nodes = [[]]
    q_values = [[]]
    q_value_indexes =[]
    seeker_locations = []
    Dummy_seekers = []
    for seeker in seekers:
        seeker_locations.append(seeker.position)
    check = []
    node_list = seekers[0].generate_nodes(station_list=[seekers[0].position])
    for node in node_list:
        if node[1] not in seeker_locations:
            check.append(node)
    node_list = check
    leaf_nodes[0] = node_list
    nodes[0] = node_list
    node_values = seekers[0].generate_node_scores(node_list=node_list, Q_values=seekers[0].q_values)
    q_values[0] = node_values

    # Create a snapshot of the state of the seekers for each move to be used later
    buffer = []
    for node in leaf_nodes[0]:
        Dummy_seeker = copy.deepcopy(seekers[0])
        Dummy_seeker.move(destination=node[1], ticket=node[2])
        buffer.append([Dummy_seeker, copy.deepcopy(seekers[1]), copy.deepcopy(seekers[2]), copy.deepcopy(seekers[3])])
    Dummy_seekers.append(buffer)

    for i in range(1, len(seekers)):
        Dummy_seekers.append([])
        leaf_nodes.append([])
        q_value_indexes.append([])
        q_values.append([])
        nodes.append([])

    while counter < N:
        seeker = seekers[agent]
        if agent == 0:
            Dummies = Dummy_seekers[agent]

            ## Selection + Expansion ##
            # For the first seeker, selection and expansion is combined since there is only one parent node to consider
            chosen_node_index, chosen_leaf_node_index, chosen_node = Selection(seeker=seeker, nodes=nodes[agent],
                                                                               leaf_nodes=leaf_nodes[agent], C=C, W=W)

            # Advance the state of the particular seeker for this specific leaf node
            (Dummies[chosen_leaf_node_index][agent]).move(destination=chosen_node[1], ticket=chosen_node[2])

            ## Simulation ##
            reward = Simulation(seekers=Dummies[chosen_leaf_node_index], player=player, chosen_move=chosen_node,
                                agent=agent, possible_location=possible_location, Round=Round, Round_limit=Round_limit,
                                coalition_reduction=r)

            ## Backpropagation ##
            current_value = q_values[agent][chosen_node_index]
            updated_value = seeker.Q_value_update(current_value=current_value, alpha=alpha, gamma=gamma, reward=reward,
                                                  list_values=[])
            q_values[agent][chosen_node_index] = updated_value
            new_identity = [chosen_node[0], chosen_node[1], chosen_node[2], updated_value]
            check = seeker.Update_Q_value_list(new_value=new_identity, Q_values=seeker.q_values)

            counter += 1
            leaf_nodes[agent][chosen_leaf_node_index] = 0
            leaf_nodes[agent + 1].append(chosen_node)

            end_sum = 0
            for i in range(len(leaf_nodes[agent])):
                if leaf_nodes[agent][i] == 0:
                    end_sum += 1
            if end_sum == len(leaf_nodes[agent]):
                agent += 1



        elif len(leaf_nodes[agent]) > 0:
            print("triggered")
            Dummies = Dummy_seekers[agent - 1]
            ## Selection ##
            chosen_node_index, chosen_leaf_node_index, chosen_node = Selection(seeker=seeker, nodes=nodes[agent],
                                                                               leaf_nodes=leaf_nodes[agent], C=C, W=W)
            ## Expansion ##
            seeker_locations = []
            chosen_state = Dummy_seekers[agent - 1][chosen_leaf_node_index]
            for state in chosen_state:
                seeker_locations.append(state.position)

            check = []
            expanded_nodes = seeker.generate_nodes(station_list=[seeker.position])
            for node in expanded_nodes:
                if node[1] not in seeker_locations:
                    check.append(node)
            expanded_nodes = check


            for i in range(len(expanded_nodes)):
                sim_node = expanded_nodes[i]
                nodes[agent].append(sim_node)
                q_value_indexes[agent-1].append(chosen_leaf_node_index)
                (Dummies[chosen_leaf_node_index][agent]).move(destination=sim_node[1], ticket=sim_node[2])
                Dummy_seekers[agent].append([Dummies[chosen_leaf_node_index][0], Dummies[chosen_leaf_node_index][1],
                                             Dummies[chosen_leaf_node_index][2], Dummies[chosen_leaf_node_index][3]])
                ## Simulation ##
                reward = Simulation(seekers=Dummies[chosen_leaf_node_index], player=player, chosen_move=sim_node,
                                    agent=agent, possible_location=possible_location, Round=Round,
                                    Round_limit=Round_limit,
                                    coalition_reduction=r)
                ## Backpropagation ##
                current_value = seeker.get_Q_value(node=sim_node, Q_values=seeker.q_values)
                future_values =[]
                future_values.append(q_values[agent-1][chosen_leaf_node_index])
                path = [i] # Use this to search in nodes

                for k in reversed(range(1,agent+1)):
                    node_before = q_value_indexes[k-1][i]
                    path.append(node_before)



            counter+=1




        else:
            agent += 1
            counter = N + 42

    return np.array(Dummy_seekers)
