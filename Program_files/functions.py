import copy
import csv
import time
from datetime import datetime

import numpy as np
import itertools

import pandas as pd

from Program_files.data_read import loc_cat


# np.random.seed(1)


def weighted_selection(categories, probabilities):
    """
    Use the provided probabilities to select a category and a station
    :param categories: list of stations in the three categories
    :param probabilities: list of probabilities for each category
    :return: chosen station
    """
    cat_list = []
    prob_list = []
    chosen = 69

    # Fill up a  list of categories and probabilities
    for i in range(len(categories)):
        category = categories[i]
        if len(category) >= 1:
            cat_list.append(i)
            prob_list.append(probabilities[i])
    prob_list = np.array(prob_list)
    total_probability = np.sum(prob_list)
    random_number = np.random.uniform(0, total_probability)
    cumulative_prob = 0

    # Make a choice based on cumulative probability
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
        print("Failure!! Empty categories given to weighted selection function")

    return station


def location_hider(player, possible_locations, loc_cat=loc_cat):
    """
    Get a possible location of the player from a list of possible locations. These are split into 3 categories and a
    weighted selection is performed to determine one station where the player can be.
    :param player: the player entity
    :param possible_locations: the previous list of possible locations
    :param loc_cat: data about the types of categories and their probabilities based on location categorisation
    :return: possible location of the player
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


    categories = [cat_1, cat_2, cat_3]
    probabilities = [loc_cat[0][0] / loc_cat[0][1], loc_cat[1][0] / loc_cat[1][1], loc_cat[2][0] / loc_cat[2][1]]
    location = weighted_selection(categories=categories, probabilities=probabilities)
    return location


def Arrange_seekers(seeker_list, player):
    """
    Creates a list of locations for the seekers to move to during the reveal round.
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
    # Use weighted selection to add stations to the list
    elif len(station_list) < len(seeker_list):
        for i in range(len(station_list)):
            target_locations.append(station_list[i])
        difference = abs(len(station_list) - len(seeker_list))

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

    # If there is any error, choose the latest combination
    if best_combination is None:
        for combo in combos:
            best_combination = combo

    chosen_targets = []
    for i in range(len(seeker_list)):
        try:
            chosen_targets.append(target_locations[best_combination[i]])
        except TypeError:
            chosen_targets.append(target_locations[i])

    return chosen_targets


def randomise_start_locations(Info, number_seekers):
    """
    Allocate random locations to seekers and player
    :param Info: Information about the stations
    :param number_seekers: number of seekers in the game
    :return: list of starting locations for the seekers and player
    """
    start_index = np.random.randint(0, len(Info), number_seekers + 1)
    while (len(set(start_index))) != len(start_index):
        start_index = np.random.randint(0, len(Info), number_seekers + 1)
    start_locations = []
    for i in range(number_seekers + 1):
        start_locations.append(Info[start_index[i]][0])
    # start_locations = [Info[start_index[0]][0],Info[start_index[1]][0], Info[start_index[2]][0], Info[start_index[3]][0] ]
    return start_locations


def write_loc_cat_file(file_name, loc_cat=loc_cat):
    """
    Update the csv file containing the location categorisatrion data
    :param file_name: name of the csv file
    :param loc_cat: data about the location categorisation
    :return:
    """
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
    """
    Write to the results file
    :param file_name: name of the results file
    :param alpha_normal: The alpha used for normal rounds
    :param gamma_normal: The gamma used for the normal rounds
    :param alpha_reveal: The alpha used for reveal rounds
    :param gamma_reveal: The gamma used for reveal rounds
    :param C: value of C used
    :param W: value of W used
    :param Caught: Boolean value showing if the seekers caught the player
    :param comments: Information about this run
    :param Rounds: Number of rounds played
    :param coverage: the average coverage of the seekers
    """
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
    date = datetime.now().strftime("%d/%m/%Y")
    data_to_add = [date, Caught, Rounds, C, W, alpha_normal, gamma_normal, alpha_reveal, gamma_reveal, coverage,
                   comments]
    read_data.loc[len(read_data)] = data_to_add
    read_data.to_csv(file_name)


def write_q_file(file_name, Q_values):
    """
    Write to the csv file containing information about the q-values for all the nodes
    :param file_name: name of the file
    :param Q_values: list containing the q-values for all the nodes
    """
    Q_Values_df = pd.DataFrame(columns=["origin", "destination", "transport", "value"])
    for entry in Q_values:
        Q_Values_df.loc[len(Q_Values_df)] = entry
    Q_Values_df.to_csv(file_name)


def update_centralised_q_values(seekers, Q_values):
    """
    Get the average of the q-values for all the seekers. These values are then written to the csv file
    :param seekers: list of seekers
    :param Q_values: the list of Q-values to be updated
    :return: Updated list of q-values
    """
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


def update_possible_location_list(possible_locations, Info, seekers, ticket, player):
    """
    Update the list of possible locations using the previous list of possible locations and the last played ticket
    :param possible_locations: original list of possible locations
    :param Info: data about all the stations
    :param seekers: list of seekers
    :param ticket: The last ticket played by the player
    :param player: the player entity
    :return: updated list of possible locations
    """
    loc_seekers = []

    # Add the last played ticket to the player's inventory
    # This makes sure that the generate_nodes function works properly
    player.tickets[ticket] += 1
    for seeker in seekers:
        loc_seekers.append(seeker.position)

    if possible_locations is None:
        ## Find every station reachable using the provided ticket if there is no original list of possible locations
        possible_locations = []
        Info_list = Info

        # If a taxi was sed then every location is possible
        if ticket == 2:
            for i in range(len(Info)):
                if Info[i][0] not in loc_seekers:
                    possible_locations.append(Info[i][0])

        else:
            for i in range(len(Info)):
                station = Info[i][0]
                bus_con = Info[i][2]
                underground_con = Info[i][3]
                taxi_con = Info[i][4]
                con = [bus_con, underground_con, taxi_con]
                if station not in loc_seekers:
                    for j in range(len(Info_list)):
                        check = False
                        target = Info_list[j][0]
                        if target in con[ticket]:
                            check = True
                        if check and target not in possible_locations and target not in loc_seekers:
                            possible_locations.append(target)
    else:
        new_list = []
        for i in range(0, len(possible_locations)):
            station = possible_locations[i]
            if station not in loc_seekers:
                nodes = player.generate_nodes([station])
                # Add the stations that can be reached from the previous station using the specific ticket to the updated list
                for node in nodes:
                    if node[1] not in new_list and node[2] == ticket and node[1] not in loc_seekers:
                        new_list.append(node[1])

        # Update the list
        if len(new_list) > 0:
            possible_locations = new_list


    # Remove any duplicates
    for station in loc_seekers:
        if station in possible_locations:
            possible_locations.remove(station)

    # Remove the previously added ticket
    player.tickets[ticket] -= 1
    return possible_locations


def Selection(seekers, leaf_nodes, C, W):
    """
    Perform UCT selection for the MCTS
    :param seekers: list of seekers
    :param leaf_nodes: list containing all the leaf nodes to select from
    :param C: value of C in the UCT equation
    :param W: value of W in the UCT equation
    :return: the index of the chosen node in the leaf nodes list, the chosen node and the agent this node belongs to
    """
    selection_scores = []
    agent_list = []
    index_list = []
    for i in range(len(leaf_nodes)):
        agent = leaf_nodes[i]
        for k in range(len(agent)):
            node = agent[k]
            if node != 0 and node != 1:
                # Only perform UCT on valid leaf nodes
                v_i = seekers[i].UCT(parent=node[0], child=node[1], transport=node[2], C=C, W=W,
                                     Q_values=seekers[i].q_values,
                                     Visits=seekers[i].visits)
                selection_scores.append(v_i)
                agent_list.append(i)
                index_list.append(k)
            else:
                selection_scores.append(-69)
                agent_list.append(i)
                index_list.append(k)

    # Choose the node with the greatest score
    chosen_leaf_node_index = np.argmax(np.array(selection_scores))
    chosen_agent = agent_list[chosen_leaf_node_index]
    chosen_index = index_list[chosen_leaf_node_index]
    chosen_node = leaf_nodes[chosen_agent][chosen_index]

    return chosen_index, chosen_node, chosen_agent


def Expansion(Dummy_seekers, agent, chosen_leaf_node_index, seeker):
    """
    Add a node to the leaf node for MCTS
    :param Dummy_seekers: list of states of the seekers
    :param agent: index of the seeker that this expansion is happening for
    :param chosen_leaf_node_index: index of the leaf node to expand
    :param seeker: the seeker that this expansion is happening for
    :return: all possible moves for this seeker for this game state
    """
    seeker_locations = []
    chosen_state = Dummy_seekers[agent][chosen_leaf_node_index]

    # Get the positions of all seeker sin this game state
    for state in chosen_state:
        seeker_locations.append(state.position)

    check = []
    expanded_nodes = seeker.generate_nodes(station_list=[seeker.position])

    # Remove already occupied nodes
    for node in expanded_nodes:
        if node[1] not in seeker_locations:
            check.append(node)
    expanded_nodes = check
    return expanded_nodes


def Simulation(seekers, player, chosen_move, agent, possible_location, Round, Round_limit, coalition_reduction):
    """
    Simulate the rest of the game for MCTS
    :param seekers: list of seekers
    :param player: the player entity
    :param chosen_move: the first move made for the seeker
    :param agent: the agent this simulation belongs to
    :param possible_location: the location being chased by the seekers
    :param Round: the round for this simulation
    :param Round_limit: the maximum number of rounds
    :param coalition_reduction: coefficient for the coalition reduction function
    :return: reward obtained after the simulation is terminated
    """
    Dummy_positions = []
    Dummies = []

    for seeker in seekers:
        # Create copies of the seekers
        # This prevents the simulation from affecting the position and ticket count of the real seekers
        Dummies.append(copy.deepcopy(seeker))
        Dummy_positions.append(seeker.position)

    reward = 0

    # Create a copy of the player entity
    Player_sim = copy.deepcopy(player)
    Player_sim.position = possible_location
    Player_sim.get_info()
    Dummies = np.array(Dummies)
    try:
        Player_sim.tickets[chosen_move[2]] += 1
    except TypeError:
        useless = 0  # This does nothing

    sim_running = True

    # Move all other seekers once
    for i in range(agent + 1, len(Dummies)):
        best_move, ticket_to_use = Dummies[i].minimise_distance(destination=possible_location,
                                                                exclude_stations=Dummy_positions, node_list=[])

        if best_move != 0:
            Dummies[i].move(destination=best_move, ticket=ticket_to_use)
            Dummy_positions[i] = best_move
            Player_sim.tickets[ticket_to_use] += 1

    # Check if the seekers caught the player after this move
    for i in range(len(Dummies)):
        if Player_sim.caught(Dummies[i]):
            sim_running = False
            if i == agent:
                reward += 2
            else:
                reward += (1 - coalition_reduction) * 2

    while sim_running:
        # THis keeps track of how many simulation rounds have happened
        counter = 1

        # Player's move
        player_moves = []
        distances = []
        for Dummy in Dummies:
            # Find out what the furthest station is for the player to move to for this dummy
            max_distance_target, transport = Player_sim.maximise_distance(target=Dummy.position,
                                                                          seeker_locs=Dummy_positions)
            if max_distance_target != 0:
                # Add this to a list of possible moves and their average distance
                player_moves.append([Player_sim.position, max_distance_target, transport])
                distances.append(
                    Player_sim.get_average_distance_difference(station_1=max_distance_target,
                                                               station_2_list=Dummy_positions))

        if len(player_moves) > 0:
            # Choose a move and move the player
            move_chosen = player_moves[np.argmax(np.array(distances))]
            Player_sim.move(destination=move_chosen[1], ticket=move_chosen[2], print_warning=True)
            possible_location = Player_sim.position

        # Seekers' move
        for i in range(len(Dummies)):
            # Move the seekers to minimise the distance between them and the player
            best_move, ticket_to_use = Dummies[i].minimise_distance(destination=possible_location,
                                                                    exclude_stations=Dummy_positions, node_list=[])
            if best_move != 0:
                Dummies[i].move(destination=best_move, ticket=ticket_to_use)
                Dummy_positions[i] = best_move
                Player_sim.tickets[ticket_to_use] += 1

            if Dummies[i].caught(Player_sim):
                sim_running = False
                if i == agent:
                    reward += 2
                else:
                    reward += (1 - coalition_reduction) * 2

        Round += 1
        counter += 1
        reward = reward / counter
        if Round > Round_limit:
            sim_running = False

    del Dummies
    del Player_sim

    return reward


def MCTS(seekers, player, Round, Round_limit, possible_location, N, C, W, r, alpha, gamma, location_list):
    """
    Run the MCTS algorithm for this location
    :param seekers: list of seekers
    :param player: player entity
    :param Round: the current round
    :param Round_limit: the maximum number of rounds
    :param possible_location: one possible location of the player
    :param N: Number of iterations for the MCTS
    :param C: value of C for the UCT
    :param W: value of W for the UCT
    :param r: value of the coalition reduction for the Simulation
    :param alpha: value of alpha for backpropagation
    :param gamma: value of gamma for backpropagation
    :return: list of moves for the seekers and the average q-value for these moves
    """
    ## Initialise ##
    start_time = time.time()
    counter = 0

    # Create a list of nodes, leaf nodes and q values
    nodes = [[]]
    expanded_node_list = [[]]
    leaf_nodes = [[]]
    q_values = [[]]
    q_value_indexes = []
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
    leaf_nodes[0] = copy.deepcopy(node_list)
    nodes[0] = copy.deepcopy(node_list)
    node_values = seekers[0].generate_node_scores(node_list=node_list, Q_values=seekers[0].q_values)
    q_values[0] = node_values

    # Create a snapshot of the state of the seekers for each move to be used later
    buffer = []
    for node in leaf_nodes[0]:
        buffer.append([copy.deepcopy(seekers[0]), copy.deepcopy(seekers[1]), copy.deepcopy(seekers[2]),
                       copy.deepcopy(seekers[3])])
    Dummy_seekers.append(buffer)

    for i in range(1, len(seekers)):
        Dummy_seekers.append([])
        leaf_nodes.append([])
        q_value_indexes.append([])
        q_values.append([])
        nodes.append([])
        expanded_node_list.append([])

    for i in range(len(leaf_nodes[0])):
        leaf_nodes[1].append(1)
        Dummy_seekers[1].append(1)
        expanded_node_list[1].append(1)

    # Check what the index of the possible location is in the list
    for i in range(len(location_list)):
        location = location_list[i]
        if location == possible_location:
            location_index = i

    while counter < N:

        ## Selection ##
        chosen_leaf_node_index, chosen_node, agent = Selection(seekers=seekers,
                                                               leaf_nodes=leaf_nodes, C=C, W=W)

        # Get the current location to search
        loc_to_simulate = copy.deepcopy(possible_location)
        if agent == 0:

            seeker = seekers[agent]
            Dummies = Dummy_seekers[agent]
            # Advance the state of the particular seeker for this specific leaf node
            try:
                (Dummies[chosen_leaf_node_index][agent]).move(destination=chosen_node[1], ticket=chosen_node[2],
                                                              print_warning=True)
            except TypeError:
                useless = 0  # This does nothing

            ## Simulation ##


            reward = Simulation(seekers=Dummies[chosen_leaf_node_index], player=player, chosen_move=chosen_node,
                                agent=agent, possible_location=loc_to_simulate, Round=Round, Round_limit=Round_limit,
                                coalition_reduction=r)

            ## Backpropagation ##
            current_value = q_values[agent][chosen_leaf_node_index]
            updated_value = seeker.Q_value_update(current_value=current_value, alpha=alpha, gamma=gamma, reward=reward,
                                                  list_values=[])

            q_values[agent][chosen_leaf_node_index] = updated_value

            counter += 1

            # Mark this leaf node as fully explored
            leaf_nodes[agent][chosen_leaf_node_index] = 0

            # Add leaf nodes for the next seeker to expand on
            leaf_nodes[agent + 1][chosen_leaf_node_index] = chosen_node
            # leaf_nodes[agent + 1].append(chosen_node)
            Dummy_seekers[agent + 1][chosen_leaf_node_index] = copy.deepcopy(Dummies[chosen_leaf_node_index])
            expanded_node_list[agent + 1][chosen_leaf_node_index] = []






        elif len(leaf_nodes[agent]) > 0 and agent <= len(seekers):
            Dummies = Dummy_seekers[agent]
            seeker = seekers[agent]

            ## Expansion ##
            expanded_nodes = Expansion(Dummy_seekers=Dummy_seekers, agent=agent,
                                       chosen_leaf_node_index=chosen_leaf_node_index, seeker=seeker)

            current_index = 0

            # Add a failsafe in case seeker is blocked on all sides
            if len(expanded_nodes) == 0:
                expanded_nodes.append(1)

            for i in range(len(expanded_nodes)):
                sim_node = expanded_nodes[i]

                # Choose a previously unchosen node and that becomes the expanded node
                if sim_node not in expanded_node_list[agent][chosen_leaf_node_index]:
                    # Add this to the list of nodes
                    nodes[agent].append(sim_node)
                    q_value_indexes[agent - 1].append(chosen_leaf_node_index)
                    try:
                        (Dummies[chosen_leaf_node_index][agent]).move(destination=sim_node[1], ticket=sim_node[2],
                                                                      print_warning=True)
                    except TypeError:
                        useless = 0  # This does nothing

                    # Add this to the expanded node list so it can not be chosen for this state again
                    expanded_node_list[agent][chosen_leaf_node_index].append(sim_node)

                    ## Simulation ##
                    # Check if a previous seeker is already at the possible target location
                    # If so, change the target location for better coverage

                    for i in range(len(Dummies[chosen_leaf_node_index])):
                        dummy = Dummies[chosen_leaf_node_index][i]
                        if dummy.position == loc_to_simulate and agent != i:
                            try:
                                loc_to_simulate = location_list[location_index + 1]
                                # print("changed location from %s to %s"%(possible_location,loc_to_simulate))
                            except IndexError:
                                loc_to_simulate = location_list[0]
                                # print("changed location from %s to %s" % (possible_location, loc_to_simulate))

                    reward = Simulation(seekers=Dummies[chosen_leaf_node_index], player=player, chosen_move=sim_node,
                                        agent=agent, possible_location=loc_to_simulate, Round=Round,
                                        Round_limit=Round_limit,
                                        coalition_reduction=r)
                    current_index = len(nodes[agent]) - 1

                    break

            ## Backpropagation ##
            try:
                current_value = seeker.get_Q_value(node=sim_node, Q_values=seeker.q_values)
                seeker.Update_visit_count(position=sim_node[1], Visits=seeker.visits)
                q_values[agent].append(current_value)
            except TypeError:
                # Only happens if a seeker is blocked on all sides
                q_values[agent].append(-10)

            # Create a path used by the q-value update function
            path = [current_index]  # Path of q_values indexes
            chosen_index = current_index
            path_values = []

            for k in reversed(range(0, agent)):
                try:
                    # Find the corresponding index in the data for the previous seeker
                    node_number = q_value_indexes[k][chosen_index]
                    path.append(node_number)
                    chosen_index = node_number
                except IndexError:
                    useless = 0  # This does nothing
            path.reverse()

            for j in range(len(path)):
                node_to_choose = path[j]
                value = q_values[j][node_to_choose]
                # Add the corresponding q-values to a list
                path_values.append(value)

            for j in range(len(path)):
                # update all the q-values in the path
                current_value = path_values[j]
                future_values = path_values[j:]
                updated_value = seekers[j].Q_value_update(current_value=current_value, alpha=alpha, gamma=gamma,
                                                          reward=reward,
                                                          list_values=future_values)
                path_values[j] = updated_value
                q_values[j][path[j]] = updated_value

            counter += 1

            if agent < len(seekers) - 1:
                # Add the chosen node as a new leaf node
                leaf_nodes[agent + 1].append(sim_node)
                # Add the updated state for the next node
                Dummy_seekers[agent + 1].append(copy.deepcopy(Dummies[chosen_leaf_node_index]))
                # Add this node to the list of nodes explored for this particular leaf node
                # This helps keep track of whether or not this leaf node is fully explored
                expanded_node_list[agent + 1].append([])

            # Undo the move made for the Simulation which updated the state
            try:
                Dummies[chosen_leaf_node_index][agent].position = sim_node[0]
                Dummies[chosen_leaf_node_index][agent].get_info()
                Dummies[chosen_leaf_node_index][agent].tickets[sim_node[2]] += 1
            except TypeError:
                useless = 0  # This does nothing

            # Remove fully explored leaf nodes
            check_sum = 0
            for node in expanded_nodes:
                if node in expanded_node_list[agent][chosen_leaf_node_index]:
                    check_sum += 1
            if check_sum == len(expanded_nodes):
                leaf_nodes[agent][chosen_leaf_node_index] = 0

        # Check if all nodes are explored
        all_done = []
        for seeker in seekers:
            all_done.append(0)
        for i in range(len(leaf_nodes)):
            node_list = leaf_nodes[i]
            length = len(node_list)
            check_sum = 0
            for node in node_list:
                if node == 0 or node == 1:
                    check_sum += 1
            if check_sum == length:
                all_done[i] = 1
        all_done = np.array(all_done)
        if np.sum(all_done) == len(seekers):
            counter = N + 42

    # Create a list of values to be checked
    final_values = q_values[0]
    chosen_index = np.argmax(final_values)
    path = [chosen_index]

    for i in range(0, len(q_value_indexes)):
        buffer = []
        buffer_index = []
        list = q_value_indexes[i]

        for k in range(len(list)):
            entry = list[k]
            if entry == chosen_index:
                buffer.append(q_values[i + 1][k])
                buffer_index.append(k)
        try:
            chosen_index = buffer_index[np.argmax(buffer)]
        except ValueError:
            # This only happens if no node is explored for this particular agent
            # Thus a random move for this agent is chosen
            nodes[i + 1] = seekers[i + 1].generate_nodes(station_list=[seekers[i + 1].position])
            chosen_index = np.random.randint(0, len(nodes[i + 1]))

        path.append(chosen_index)

    chosen_node = []
    chosen_q = []

    # Choose the list of moves with the highest q-values
    for i in range(len(path)):
        chosen_node.append(nodes[i][path[i]])
        try:
            chosen_q.append(q_values[i][path[i]])
        except IndexError:
            sub_value = seekers[i].get_Q_value(node=nodes[i][path[i]], Q_values=seekers[i].q_values)
            chosen_q.append(sub_value)

    average = np.average(chosen_q)
    end_time = time.time()
    del Dummy_seekers
    return chosen_node, average
