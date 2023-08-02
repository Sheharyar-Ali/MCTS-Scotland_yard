import numpy as np
from data_read import Info, Q_values, Visits, loc_cat
from functions import *
import copy
from enum import Enum


class Ticket(Enum):
    Bus = 0
    Underground = 1
    Taxi = 2


class Player:
    def __init__(self, role, position, tickets):
        self.taxi_connections = None
        self.underground_connections = None
        self.bus_connections = None
        self.connections = None
        self.role = role  # string
        self.position = position  # int
        self.tickets = tickets  # [bus,underground,taxi] (int)
        self.get_info()
        if self.role == "seeker":
            self.visits = copy.deepcopy(Visits)
            self.q_values = copy.deepcopy(Q_values)
            self.coverage = 0

    def get_info(self, Info=Info):
        for i in range(len(Info)):
            if Info[i][0] == self.position:
                self.bus_connections = Info[i][2]
                self.underground_connections = Info[i][3]
                self.taxi_connections = Info[i][4]
        self.connections = [self.bus_connections, self.underground_connections, self.taxi_connections]

    def can_move(self, destination, ticket, print_warning=False):
        """
        Checks if the requested move is legal
        :param destination: id of the destination station
        :param ticket: type of ticket to use (0=bus, 1 = underground, 2= taxi)
        :param print_warning: If you want to print out why the move failed
        :return: True or False
        """

        if destination in self.connections[ticket] and self.tickets[ticket] > 0:
            return True
        elif self.tickets[ticket] <= 0 and print_warning:
            print("Insufficient tickets for this move")
        elif print_warning:
            print("Can not move to new station from current station")

        return False

    def caught(self, other_player):
        """
        Check if you made contact with seeker
        :param other_player: Seeker
        :return: Boolean value indicating if player has been caught
        """
        if self.position == other_player.position:
            return True
        return False

    def move(self, destination, ticket, print_warning=False):
        """
        Move to target location. Updates the connections of the entity
        :param destination: Target station
        :param ticket: Ticket used to get to target station
        :return: N/A
        """
        if self.can_move(destination=destination, ticket=ticket, print_warning=print_warning):
            self.position = destination
            self.tickets[ticket] -= 1
            self.get_info()
            if self.position == "player":
                print("Player moved to station: ", self.position)
        elif print_warning:
            print("Could not move entity")

    def get_station_info(self, station, Info=Info):
        """
        Get all information about a station
        :param station: the station required
        :param Info: List containing data on all stations
        :return: List containing the data of a particular station
        """
        required = 0
        for stations in Info:
            if stations[0] == station:
                required = stations
        return required

    def update_loc_cat(self, player, location_list, loc_cat=loc_cat):
        """
        Updates the location categorisation information
        :return: None
        """
        for location in location_list:
            chosen_station_info = self.get_station_info(station=location)
            if chosen_station_info[3] != [0]:
                loc_cat[2][1] += 1
            elif chosen_station_info[2] != [0]:
                loc_cat[1][1] += 1
            else:
                loc_cat[0][1] += 1

        player_station_info = self.get_station_info(station=player.position)
        if player_station_info[3] != [0]:
            loc_cat[2][0] += 1
        elif player_station_info[2] != [0]:

            loc_cat[1][0] += 1
        else:
            loc_cat[0][0] += 1

    def get_coverage(self, visit_count):
        """
        Get the percentage of stations that have been visited at least once by a seeker
        :param visit_count: list of the visit counts of each station for this seeker
        :return: percentage explored
        """
        unexplored = 0
        explored = 0
        for visit in visit_count:
            if visit[1] == 0:
                unexplored += 1
            else:
                explored += 1
        total_explored = explored / (unexplored + explored)
        return total_explored

    def get_remaining_nodes(self, station, node_list, exclusion_list):
        """
        Get a list of all unexplored nodes from an origin station
        :param station: The origin station
        :param node_list: list of already explored nodes
        :param exclusion_list: list of stations that you should not move to
        :return:
        """
        generated_nodes = self.generate_nodes(station_list=[station])
        to_remove = []
        for node in generated_nodes:
            if node in node_list or node[1] in exclusion_list:
                to_remove.append(node)
        for node in to_remove:
            generated_nodes.remove(node)
        return generated_nodes

    def get_distance_difference(self, station_1, station_2, print_info=False):
        station_1_info = self.get_station_info(station=station_1)
        station_2_info = self.get_station_info(station=station_2)
        delta_x = abs(station_1_info[1][0] - station_2_info[1][0])
        delta_y = abs(station_1_info[1][1] - station_2_info[1][1])
        if print_info:
            print("stations", station_1, station_2)
            print("info", station_1_info, station_2_info)
            print("delats", delta_x, delta_y)
        difference = np.sqrt(delta_x ** 2 + delta_y ** 2)
        return difference

    def minimise_distance(self, destination, node_list, exclude_stations=None):
        """
        Get the node that minimises the distance between you and a target destination
        :param destination: target destination
        :param node_list: list of already explored nodes
        :param exclude_stations: list of stations you should not move to
        :return: The station you should move to and what transportation you should use
        """
        if exclude_stations is not None:
            valid_nodes = self.get_remaining_nodes(station=self.position, node_list=node_list,
                                                   exclusion_list=exclude_stations)
        else:
            valid_nodes = self.generate_nodes(station_list=[self.position])

        difference = []
        possible_station = []
        ticket_list = []
        for node in valid_nodes:
            if self.can_move(destination=node[1], ticket=node[2]):
                difference.append(self.get_distance_difference(station_1=node[1], station_2=destination))
                ticket_list.append(node[2])
                possible_station.append(node[1])

        difference = np.array(difference)
        if len(difference) != 0:
            chosen = possible_station[np.argmin(difference)]
            ticket_used = ticket_list[np.argmin(difference)]

        else:
            chosen = 0
            ticket_used = 0

        return chosen, ticket_used

    def maximise_distance(self, target):
        """
        Find the optimum station to move to, to maximise distance between you and a target station
        :param target: Station you want to move the furthest away from
        :return: Station to move to
        """
        valid_nodes = self.generate_nodes(station_list=[self.position])

        difference = []
        possible_station = []
        ticket_list = []

        for node in valid_nodes:
            if self.can_move(destination=node[1], ticket=node[2]):
                difference.append(self.get_distance_difference(station_1=node[1], station_2=target))
                ticket_list.append(node[2])
                possible_station.append(node[1])

        difference = np.array(difference)
        if len(difference) != 0:
            chosen = possible_station[np.argmax(difference)]
            ticket_used = ticket_list[np.argmax(difference)]
        else:
            chosen = 0
            ticket_used = 0
        return chosen, ticket_used

    def UCT(self, parent, child, transport, C, W, Q_values, Visits):
        scores = []
        x_i = 0
        n_p = 0
        n_i = 0
        for i in range(len(Q_values)):
            if Q_values[i][0] == parent and Q_values[i][1] == child and Q_values[i][2] == transport:
                x_i = Q_values[i][3]
            if Q_values[i][0] == parent and Q_values[i][1] == child:
                scores.append(Q_values[i][3])
        scores = np.array(scores)
        for i in range(len(Visits)):
            if Visits[i] == parent:
                n_p = Visits[i][1]
            if Visits[i] == child:
                n_i = Visits[i][1]

        x_a = np.average(scores)
        if n_i != 0:
            V = x_i + (C * np.sqrt(np.log(n_p) / n_i)) + (W * (x_a / (n_i * (1 - x_i) + 1)))
        else:
            V = x_i + (W * (x_a / (n_i * (1 - x_i) + 1)))  # Prevents divison by 0 at the start of the game

        return V

    def generate_nodes(self, station_list, Info=Info):
        """
        Generate a list of possible nodes from the required station. This is used in the MCTS
        :param station_list: List of stations from which to generate the nodes
        :param Info: Information about the stations
        :return: List containing the nodes in the format [[origin_1, destination_1, ticket_used_1], ..., [origin_i, destination_i, ticket_used_i]]
        """
        nodes = []
        tickets_available = []
        for i in range(len(self.tickets)):
            ticket = self.tickets[i]
            if ticket > 0:
                tickets_available.append(i)

        for i in range(len(Info)):
            station = Info[i]
            for ticket in tickets_available:
                if station[0] in station_list and station[ticket + 2] != [0]:
                    for entries in station[ticket + 2]:
                        nodes.append([station[0], entries, ticket])

        return nodes

    def generate_node_scores(self, node_list, Q_values):
        node_scores = []
        for i in range(len(node_list)):
            node = node_list[i]
            for j in range(len(Q_values)):
                if Q_values[j][0] == node[0] and Q_values[j][1] == node[1] and Q_values[j][2] == node[2]:
                    node_scores.append(Q_values[j][3])

        return node_scores

    def get_Q_value(self, node, Q_values):
        value = 0
        for q_value in Q_values:
            if q_value[0] == node[0] and q_value[1] == node[1] and q_value[2] == node[2]:
                value = q_value[3]
        return value

    def Update_Q_value_list(self, new_value, Q_values):
        index = 0
        for i in range(len(Q_values)):
            if new_value[0] == Q_values[i][0] and new_value[1] == Q_values[i][1] and new_value[2] == Q_values[i][2]:
                index = i
                Q_values[i] = new_value
                break

        return index

    def Q_value_update(self, current_value, alpha, gamma, reward, list_values):
        if len(list_values) != 0:
            future_q = max(list_values)
        else:
            future_q = 0
        updated_value = (1 - alpha) * current_value + alpha * (reward + gamma * future_q)

        return updated_value

    def Update_visit_count(self, position, Visits):
        index = 0
        for i in range(len(Visits)):
            if Visits[i][0] == position:
                Visits[i][1] += 1
                index = i
                break

        return index

    def generate_path(self, node_list):
        path_list = []
        path_list_indexed = []
        path_index = []
        for i in range(len(node_list)):
            node = node_list[i]
            path_list.append([node[0], node[1]])
            path_list_indexed.append([i])
            path_index.append(i)
        return path_list_indexed, path_index, path_list

    def all_full_connections(self, station, node_list):
        """
        See if all of the connections of a station have been explored
        :param station: station to check
        :param node_list: list of already explored nodes
        :return: True if node is fully explored
        """
        generated_nodes = self.generate_nodes(station_list=[station])
        length = len(generated_nodes)
        check = 0
        for node in generated_nodes:
            if node in node_list:
                check += 1
        if check == length:
            return True
        else:
            return False

    def distance_based_reward(self, player_location, reward_multiplier):
        distance = self.get_distance_difference(station_1=self.position, station_2=player_location)
        if distance != 0:
            reward = reward_multiplier / distance  # Higher rewards for lower distances
        else:
            reward = 0
        return reward

    def MCTS(self, N, player, seekers, C, W, alpha, gamma, possible_locations):
        counter = 0
        exclusion_list = []
        for seeker in seekers:
            if seeker.position not in exclusion_list:
                exclusion_list.append(seeker.position)  # Make seeker unable to move to occupied stations
        nodes = self.generate_nodes(station_list=[self.position])  # List of nodes in the tree
        for node in nodes:
            if node[1] in exclusion_list:
                nodes.remove(node)  # Remove nodes that are already occupied by other seekers

        node_q_values = self.generate_node_scores(node_list=nodes,
                                                  Q_values=self.q_values)  # The q-values of all the nodes in the tree
        leaf_nodes = self.generate_nodes(station_list=[self.position])  # List of leaf nodes

        path_list_indexed, path_index, path_list = self.generate_path(node_list=nodes)

        error_counter = 0

        if len(leaf_nodes) == 0:
            counter = N + 10
            Best_move = [0, 0, 0]
        else:
            Best_move = 0

        while counter < N:
            sim_running = True
            run_backprop = True
            self.coverage = self.get_coverage(visit_count=self.visits)

            ## Initialise ##
            node_scores = []  # The scores of all the leaf nodes in the tree (For Selection)
            possible_location = location_hider(player=player, possible_locations=possible_locations)
            Dummy_player = copy.deepcopy(player)  # Create a Dummy player to use for the simulation
            Dummy_player.position = possible_location
            Dummy_player.get_info()

            ## Selection ##

            for node in leaf_nodes:
                v_i = self.UCT(parent=node[0], child=node[1], transport=node[2], C=C, W=W, Q_values=self.q_values,
                               Visits=self.visits)
                node_scores.append(v_i)
            chosen_node_index = np.argmax(np.array(node_scores))  # The index of the chosen node in leaf_nodes list
            chosen_node = leaf_nodes[chosen_node_index]
            chosen_node_index_full = 0  # The index of the chosen node in the nodes list
            for i in range(len(nodes)):
                node = nodes[i]
                if chosen_node == node:
                    chosen_node_index_full = i

            Dummy_seeker = copy.deepcopy(self)  # Create a dummy seeker to use for the simulation
            Dummy_seeker.position = chosen_node[1]
            Dummy_seeker.get_info()
            exclusion_list.append(chosen_node[0])  # Add the origin to the list

            ## Expansion ##
            # print("leaf", leaf_nodes)
            # print("nodes", nodes)
            # print("Selected node:", chosen_node, Dummy_seeker.position)
            expanded_node, ticket_used = Dummy_seeker.minimise_distance(destination=possible_location,
                                                                        exclude_stations=exclusion_list,
                                                                        node_list=nodes)

            new_node = [chosen_node[1], expanded_node, ticket_used]
            # print("trying to add:", new_node)

            if expanded_node == 0:
                new_node = nodes[-1]

            # print("exclusion list", exclusion_list)
            if new_node not in nodes:
                new_node_q_value = self.generate_node_scores(node_list=[new_node], Q_values=self.q_values)[0]
                nodes.append(new_node)  # Add to the tree
                leaf_nodes.append(new_node)  # Add to list of leaf nodes
                node_q_values.append(new_node_q_value)
                leaf_nodes.pop(chosen_node_index)  # Remove from leaf node so the UCT can not run on the parent node
                check_full_connections = self.all_full_connections(station=new_node[0],
                                                                   node_list=nodes)  # See if this node has any more connections left to explore
                if check_full_connections:
                    exclusion_list.append(new_node[0])
                # print("node added", new_node)
                error_counter = 0

            else:
                sim_running = False
                # print("No unique nodes can be added")
                run_backprop = False
                error_counter += 1

            ## Simulation ##

            Dummy_seeker.move(destination=expanded_node, ticket=ticket_used)
            while sim_running:
                player_target, player_ticket = Dummy_player.maximise_distance(Dummy_seeker.position)
                if player_target != 0:
                    Dummy_player.move(destination=player_target, ticket=player_ticket)
                dummy_target, dummy_ticket = Dummy_seeker.minimise_distance(destination=Dummy_player.position,
                                                                            node_list=nodes)
                if dummy_target != 0:
                    Dummy_seeker.move(destination=dummy_target, ticket=dummy_ticket)
                    Dummy_player.tickets[dummy_ticket] += 1
                else:
                    sim_running = False
                if Dummy_player.caught(Dummy_seeker) or np.sum(np.array(Dummy_seeker.tickets)) == 0:
                    sim_running = False
                    # if Dummy_player.caught(Dummy_seeker):
                    #     print("SIM ENDED BECAUSE MR X CAUGHT")
            # print("Simulation done")
            Dummy_seeker.tickets = self.tickets

            ## Backpropagation ##
            if run_backprop:
                if Dummy_player.caught(Dummy_seeker):
                    reward = 1
                else:
                    reward = -1
                node_path_index = path_index[chosen_node_index_full]  # Find which of the paths this node gets added to
                path_index.append(node_path_index)  # Add it to the list of indexes for each path
                node_path = path_list_indexed[
                    node_path_index]  # get the list of indexes of the nodes in the appropriate path
                node_path.append(chosen_node_index_full)  # Add to the list of indexes
                path_list_indexed[node_path_index] = node_path
                path_list[node_path_index].append(new_node[1])  # Add the node id to the list of the path

                for i in range(len(node_path)):
                    index = node_path[i]
                    current_value = node_q_values[index]
                    list_future_values = node_q_values[i:]
                    updated_value = self.Q_value_update(current_value=current_value, alpha=alpha, gamma=gamma,
                                                        reward=reward,
                                                        list_values=list_future_values)
                    node_q_values[index] = updated_value
                    new_identity = [nodes[index][0], nodes[index][1], nodes[index][2], updated_value]
                    check = self.Update_Q_value_list(new_value=new_identity, Q_values=self.q_values)

                    if i == 0:

                        check_2 = self.Update_visit_count(position=nodes[index][0], Visits=self.visits)

                        check_3 = self.Update_visit_count(position=nodes[index][1], Visits=self.visits)
                    else:
                        check_2 = self.Update_visit_count(position=nodes[index][0], Visits=self.visits)

            ## Remove fully explored nodes from leaf node list
            for check_node in leaf_nodes:
                # print("End check")
                remaining_nodes = self.get_remaining_nodes(station=check_node[1], node_list=nodes,
                                                           exclusion_list=exclusion_list)
                # print("Remaining nodes for ", check_node, remaining_nodes, exclusion_list)
                if self.all_full_connections(station=check_node[1], node_list=nodes):
                    # print("Removing at end of iteration: ", check_node)
                    leaf_nodes.remove(check_node)
                elif len(remaining_nodes) == 0:
                    # print("Removing at end of iteration: ", check_node, remaining_nodes)
                    leaf_nodes.remove(check_node)

            exclusion_list.pop(-1)  # remove origin from the excluded list
            # print("End iteration", counter)
            # print("path list",path_list)
            if error_counter < 5 and len(leaf_nodes) > 0:
                counter += 1

            else:
                # print("Total iterations done", counter + 1)
                # print("parents", len(exclusion_list))
                counter = N + 1

        if Best_move != [0, 0, 0]:
            parent = self.position
            values = []
            values_index = []
            for i in range(len(nodes)):
                node = nodes[i]
                if node[0] == parent:
                    values.append(self.get_Q_value(node=node, Q_values=self.q_values))
                    values_index.append(i)
            values = np.array(values)
            Best_index = values_index[np.argmax(values)]
            Best_move = nodes[Best_index]

        ## If no moves possible
        if Best_move == [0, 0, 0]:
            print("Seeker unable to move!!!")

        return Best_move

    def MCTS_reveal_round(self, N, possible_location, player, seekers, C, W, alpha, gamma, reward_multiplier):
        Best_move = 0
        error_counter = 0
        exclusion_list = []
        for seeker in seekers:
            if seeker.position not in exclusion_list:
                exclusion_list.append(seeker.position)  # Make seeker unable to move to occupied stations
        nodes = self.generate_nodes(station_list=[self.position])  # List of nodes in the tree
        for node in nodes:
            if node[1] in exclusion_list:
                nodes.remove(node)  # Remove nodes that are already occupied by other seekers

        node_q_values = self.generate_node_scores(node_list=nodes,
                                                  Q_values=self.q_values)  # The q-values of all the nodes in the tree
        leaf_nodes = self.generate_nodes(station_list=[self.position])  # List of leaf nodes

        path_list_indexed, path_index, path_list = self.generate_path(node_list=nodes)

        # Check if you can already reach the player
        for node in nodes:
            if node[1] == player.position:
                Best_move = node

        # Check if seeker can actually move from current position
        if len(leaf_nodes) == 0:
            counter = N + 10
            Best_move = [0, 0, 0]

        if Best_move == 0:
            counter = 0
        else:
            counter = N + 10

        while counter < N:
            sim_running = True
            run_backprop = True
            self.coverage = self.get_coverage(visit_count=self.visits)

            ## Initialise ##
            node_scores = []  # The scores of all the leaf nodes in the tree (For Selection)
            # possible_location = location_hider(Info=Info, ticket=last_ticket, seekers=seeker_list)
            Dummy_player = copy.deepcopy(player)  # Create a Dummy player to use for the simulation
            Dummy_player.position = possible_location
            Dummy_player.get_info()

            ## Selection ##
            for node in leaf_nodes:
                v_i = self.UCT(parent=node[0], child=node[1], transport=node[2], C=C, W=W, Q_values=self.q_values,
                               Visits=self.visits)
                node_scores.append(v_i)
            chosen_node_index = np.argmax(np.array(node_scores))  # The index of the chosen node in leaf_nodes list
            chosen_node = leaf_nodes[chosen_node_index]
            chosen_node_index_full = 0  # The index of the chosen node in the nodes list
            for i in range(len(nodes)):
                node = nodes[i]
                if chosen_node == node:
                    chosen_node_index_full = i

            Dummy_seeker = copy.deepcopy(self)  # Create a dummy seeker to use for the simulation
            Dummy_seeker.position = chosen_node[1]
            Dummy_seeker.get_info()
            exclusion_list.append(chosen_node[0])  # Add the origin to the list

            ## Expansion ##
            # print("leaf", leaf_nodes)
            # print("nodes", nodes)
            # print("Selected node:", chosen_node, Dummy_seeker.position)
            expanded_node, ticket_used = Dummy_seeker.minimise_distance(destination=possible_location,
                                                                        exclude_stations=exclusion_list,
                                                                        node_list=nodes)

            new_node = [chosen_node[1], expanded_node, ticket_used]
            # print("trying to add:", new_node)

            if expanded_node == 0:
                new_node = nodes[-1]

            # print("exclusion list", exclusion_list)
            if new_node not in nodes:
                new_node_q_value = self.generate_node_scores(node_list=[new_node], Q_values=self.q_values)[0]
                nodes.append(new_node)  # Add to the tree
                leaf_nodes.append(new_node)  # Add to list of leaf nodes
                node_q_values.append(new_node_q_value)
                leaf_nodes.pop(chosen_node_index)  # Remove from leaf node so the UCT can not run on the parent node
                check_full_connections = self.all_full_connections(station=new_node[0],
                                                                   node_list=nodes)  # See if this node has any more connections left to explore
                if check_full_connections:
                    exclusion_list.append(new_node[0])
                # print("node added", new_node)
                error_counter = 0

            else:
                sim_running = False
                # print("No unique nodes can be added")
                run_backprop = False
                error_counter += 1

            ## Simulation ##

            Dummy_seeker.move(destination=expanded_node, ticket=ticket_used)
            while sim_running:
                player_target, player_ticket = Dummy_player.maximise_distance(Dummy_seeker.position)
                if player_target != 0:
                    Dummy_player.move(destination=player_target, ticket=player_ticket)
                dummy_target, dummy_ticket = Dummy_seeker.minimise_distance(destination=Dummy_player.position,
                                                                            node_list=nodes)
                if dummy_target != 0:
                    Dummy_seeker.move(destination=dummy_target, ticket=dummy_ticket)
                    Dummy_player.tickets[dummy_ticket] += 1
                else:
                    sim_running = False
                if Dummy_player.caught(Dummy_seeker) or np.sum(np.array(Dummy_seeker.tickets)) == 0:
                    sim_running = False
                    # if Dummy_player.caught(Dummy_seeker):
                    #     print("SIM ENDED BECAUSE MR X CAUGHT")
            # print("Simulation done")
            Dummy_seeker.tickets = self.tickets

            ## Backpropagation ##
            if run_backprop:
                reward = self.distance_based_reward(player_location=Dummy_player.position,
                                                    reward_multiplier=reward_multiplier)

                node_path_index = path_index[chosen_node_index_full]  # Find which of the paths this node gets added to
                path_index.append(node_path_index)  # Add it to the list of indexes for each path
                node_path = path_list_indexed[
                    node_path_index]  # get the list of indexes of the nodes in the appropriate path
                node_path.append(chosen_node_index_full)  # Add to the list of indexes
                path_list_indexed[node_path_index] = node_path
                path_list[node_path_index].append(new_node[1])  # Add the node id to the list of the path

                for i in range(len(node_path)):
                    index = node_path[i]
                    current_value = node_q_values[index]
                    list_future_values = node_q_values[i:]
                    updated_value = self.Q_value_update(current_value=current_value, alpha=alpha, gamma=gamma,
                                                        reward=reward,
                                                        list_values=list_future_values)
                    node_q_values[index] = updated_value
                    new_identity = [nodes[index][0], nodes[index][1], nodes[index][2], updated_value]
                    check = self.Update_Q_value_list(new_value=new_identity, Q_values=self.q_values)

                    if i == 0:

                        check_2 = self.Update_visit_count(position=nodes[index][0], Visits=self.visits)

                        check_3 = self.Update_visit_count(position=nodes[index][1], Visits=self.visits)
                    else:
                        check_2 = self.Update_visit_count(position=nodes[index][0], Visits=self.visits)

            ## Remove fully explored nodes from leaf node list
            for check_node in leaf_nodes:
                # print("End check")
                remaining_nodes = self.get_remaining_nodes(station=check_node[1], node_list=nodes,
                                                           exclusion_list=exclusion_list)
                # print("Remaining nodes for ", check_node, remaining_nodes, exclusion_list)
                if self.all_full_connections(station=check_node[1], node_list=nodes):
                    # print("Removing at end of iteration: ", check_node)
                    leaf_nodes.remove(check_node)
                elif len(remaining_nodes) == 0:
                    # print("Removing at end of iteration: ", check_node, remaining_nodes)
                    leaf_nodes.remove(check_node)

            exclusion_list.pop(-1)  # remove origin from the excluded list
            # print("End iteration", counter)
            # print("path list",path_list)
            if error_counter < 5 and len(leaf_nodes) > 0:
                counter += 1

            else:
                # print("Total iterations done", counter + 1)
                # print("parents", len(exclusion_list))
                # print("nodes" , nodes)
                counter = N + 1

        ## If you cant already reach the player, determine best move
        if Best_move == 0:
            parent = self.position
            values = []
            values_index = []
            for i in range(len(nodes)):
                node = nodes[i]
                if node[0] == parent:
                    values.append(self.get_Q_value(node=node, Q_values=self.q_values))
                    values_index.append(i)
            values = np.array(values)
            Best_index = values_index[np.argmax(values)]
            Best_move = nodes[Best_index]

        ## If no moves possible
        if Best_move == [0, 0, 0]:
            print("Seeker unable to move!!!")

        return Best_move

    def RL_Backprop(self, move_made, reward_multiplier, alpha, gamma):
        new_coverage = self.get_coverage(visit_count=self.visits)
        reward = reward_multiplier * (new_coverage - self.coverage)
        nodes = self.generate_nodes(station_list=[self.position])
        future_q_values = self.generate_node_scores(node_list=nodes, Q_values=self.q_values)
        current_value = self.get_Q_value(node=move_made, Q_values=self.q_values)
        updated_value = self.Q_value_update(current_value=current_value, alpha=alpha, gamma=gamma, reward=reward,
                                            list_values=future_q_values)
        new_identity = [move_made[0], move_made[1], move_made[2], updated_value]
        self.Update_Q_value_list(new_value=new_identity, Q_values=self.q_values)
