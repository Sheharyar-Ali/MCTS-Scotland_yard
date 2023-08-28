import numpy as np
from Program_files.data_read import Info, Q_values, Visits, loc_cat
from Program_files.functions import *
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

        # These are useful only for the seekers
        self.visits = copy.deepcopy(Visits)
        self.real_visits = copy.deepcopy(Visits)
        self.q_values = copy.deepcopy(Q_values)
        self.coverage = 0
        self.real_coverage = 0

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
            print(self.position, destination, ticket)

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
        Move to target location. Updates the connections of the entity.
        :param destination: Target station
        :param ticket: Ticket used to get to target station
        :param print_warning: Boolean indicating if the errors should be printed

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
        Updates the location categorisation data
        :param player: player entity
        :param location_list: list of locations
        :param loc_cat: data about the location categorisation
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


    def get_real_coverage(self):
        """
        Get the percentage of stations that have been visited at least once by the seeker during the actual game
        :return: percentage explored
        """
        unexplored = 0
        explored = 0
        visit_count = self.real_visits
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
        """
        Get the absolute difference between two stations
        :param station_1: the first station
        :param station_2: the second station
        :param print_info: Boolean indicating if information needs to be printed
        :return: absolute difference between station 1 and 2
        """
        station_1_info = self.get_station_info(station=station_1)
        station_2_info = self.get_station_info(station=station_2)
        if print_info:
            print("stations", station_1, station_2)
            print("info", station_1_info, station_2_info)
            # print("delats", delta_x, delta_y)
        delta_x = abs(station_1_info[1][0] - station_2_info[1][0])
        delta_y = abs(station_1_info[1][1] - station_2_info[1][1])

        difference = np.sqrt(delta_x ** 2 + delta_y ** 2)
        return difference

    def get_average_distance_difference(self, station_1, station_2_list, print_info=False):
        """
        Get the average difference between station 1 and a list of other stations
        :param station_1: station 1
        :param station_2_list: list of stations
        :param print_info: Boolean indicating if information needs to be printed
        :return: average difference in distance
        """
        list = []
        for i in range(len(station_2_list)):
            station_1_info = self.get_station_info(station=station_1)
            station_2_info = self.get_station_info(station=station_2_list[i])
            if print_info:
                print("stations", station_1, station_2_list[i])
                print("info", station_1_info, station_2_info)
                # print("delats", delta_x, delta_y)
            delta_x = abs(station_1_info[1][0] - station_2_info[1][0])
            delta_y = abs(station_1_info[1][1] - station_2_info[1][1])

            difference = np.sqrt(delta_x ** 2 + delta_y ** 2)
            list.append(difference)

        return np.average(np.array(list))

    def minimise_distance(self, destination, node_list, exclude_stations=None):
        """
        Get the node that minimises the distance between you and a target destination
        :param destination: target destination
        :param node_list: list of already explored nodes
        :param exclude_stations: list of stations you can not move to
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

    def maximise_distance(self, target, seeker_locs):
        """
        Find the optimum station to move to, to maximise distance between you and a target station
        :param seeker_locs: position of the seekers
        :param target: Station you want to move the furthest away from
        :return: Station to move to
        """
        valid_nodes = self.generate_nodes(station_list=[self.position])
        safe_nodes = []
        # Ensure that you cant move to where a seeker is located
        for node in valid_nodes:
            if node[1] not in seeker_locs:
                safe_nodes.append(node)
        valid_nodes = safe_nodes

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
        """
        Calculate the scores of the node based on UCT
        :param parent: parent station (origin)
        :param child: child station (destination)
        :param transport: type of ticket used
        :param C: value of C
        :param W: value of W
        :param Q_values: list of q-values
        :param Visits: list containing the visit counts of all the stations
        :return: UCT score for this node
        """
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
        """
        Get a list of Q-values for the nodes in a list
        :param node_list: list of nodes
        :param Q_values: list of Q-values for all the nodes
        :return: list containing Q-values for the chosen list of nodes
        """
        node_scores = []
        for i in range(len(node_list)):
            node = node_list[i]
            for j in range(len(Q_values)):
                if Q_values[j][0] == node[0] and Q_values[j][1] == node[1] and Q_values[j][2] == node[2]:
                    node_scores.append(Q_values[j][3])
        return node_scores

    def get_Q_value(self, node, Q_values):
        """
        Get the Q value for a single node
        :param node: chosen node
        :param Q_values: list containing Q-values for all the nodes
        :return: the Q-value for this node
        """
        value = 0
        for q_value in Q_values:
            if q_value[0] == node[0] and q_value[1] == node[1] and q_value[2] == node[2]:
                value = q_value[3]
        return value

    def Update_Q_value_list(self, new_value):
        """
        Update a seeker's Q-value list
        :param new_value: new Q-value
        :param Q_values: the list of Q-values to update
        :return: the index of this particular Q-valyue (used for testing)
        """
        index = 0
        Q_values = self.q_values
        for i in range(len(Q_values)):
            if new_value[0] == Q_values[i][0] and new_value[1] == Q_values[i][1] and new_value[2] == Q_values[i][2]:
                index = i
                Q_values[i] = new_value
                break

        return index

    def Q_value_update(self, current_value, alpha, gamma, reward, list_values):
        """
        Use the Q-value update equation to find the new Q-value for a node
        :param current_value: the node's curren value
        :param alpha: alpha
        :param gamma: gamma
        :param reward: reward obtained
        :param list_values: list of future Q-values
        :return: the new value for this node
        """
        if len(list_values) != 0:
            future_q = max(list_values)
        else:
            future_q = 0
        updated_value = (1 - alpha) * current_value + alpha * (reward + gamma * future_q)

        return updated_value

    def Update_visit_count(self, position, Visits):
        """
        Update the visit count for this seeker
        :param position: the location to update
        :param Visits: the list of visits to update
        :return: index of this location in the list (Used for testing)
        """
        index = 0
        for i in range(len(Visits)):
            if Visits[i][0] == position:
                Visits[i][1] += 1
                index = i
                break

        return index


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
        """
        Calculate a reward based on the distance between the entity and a player location
        :param player_location: location of the player
        :param reward_multiplier: multiplier for the reward equation
        :return: the calculated reward
        """
        distance = self.get_distance_difference(station_1=self.position, station_2=player_location)
        if distance != 0:
            reward = reward_multiplier / distance  # Higher rewards for lower distances
        else:
            reward = 0
        return reward

    def Movement_Reveal_Round(self, possible_location, seekers, player, alpha, gamma, reward_multiplier):
        """
        Handle everything related to the movement of the seekers in a reveal round
        :param possible_location: location of the player
        :param seekers: list of seekers
        :param player: player entity
        :param alpha: alpha for the Q-value update equation
        :param gamma: gamma for the Q-value update function
        :param reward_multiplier: multiolier for the reward
        """
        Best_move = 0
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
        # Check if you can already reach the player
        for node in nodes:
            if node[1] == player.position:
                Best_move = node

        if Best_move == 0:
            expanded_node, ticket_used = self.minimise_distance(destination=possible_location,
                                                                exclude_stations=exclusion_list,
                                                                node_list=[])
            if expanded_node != 0:
                Best_move = [self.position, expanded_node, ticket_used]
            else:
                # Make a random move to try and move
                for node in nodes:
                    if self.can_move(destination=node[1], ticket=node[2]):
                        Best_move = node

        try:
            self.move(destination=Best_move[1], ticket=Best_move[2])
            print("Seeker moved to ", Best_move[1])
            self.Update_visit_count(position=Best_move[1], Visits=self.real_visits)
        except TypeError:
            print("Seeker has no viable moves")

        ## Backpropagation ##
        reward = self.distance_based_reward(player_location=player.position,
                                            reward_multiplier=reward_multiplier)
        for i in range(len(nodes)):
            node = nodes[i]
            if node == Best_move:
                current_value = node_q_values[i]
                alpha = alpha
                gamma = gamma
                updated_value = self.Q_value_update(current_value=current_value, alpha=alpha, gamma=gamma,
                                                    reward=reward, list_values=[])
                new_identity = [node[0], node[1], node[2], updated_value]
                check = self.Update_Q_value_list(new_value=new_identity)

    def total_coverage(self, seekers):
        """
        Calculate the total coverage achieved by all the seekers
        :param seekers:
        :return: total coverage
        """
        stats = []
        for location in seekers[0].visits:
            stats.append(0)
        for seeker in seekers:
            for i in range(len(seeker.real_visits)):
                location = seeker.real_visits[i]
                if location[1] > 0 and stats[i] == 0:
                    stats[i] = 1
        coverage = np.sum(stats) / len(seekers[0].real_visits)
        return coverage

    def loc_cat_reward(self, categories):
        """
        Calculate the probability of a player being at a certain category of stations
        :param categories: list of categories
        :return: probability
        """
        station_info = self.get_station_info(station=self.position)
        bus_con = station_info[2]
        underground_con = station_info[3]
        if underground_con != [0]:
            category = 2
        elif bus_con != [0]:
            category = 1
        else:
            category = 0
        probability = categories[category][0] / (categories[0][0] + categories[1][0] + categories[2][0])

        return probability

    def avoid_area_reward(self, possible_locations, chosen_node):
        """
        Calculate the cheange in difference between a seeker and  possible locations of a player after a move
        :param possible_locations: list of possible locations
        :param chosen_node: the last move made by the seeker
        :return: the change in average distance due to this move
        """
        distances_original = []
        distances_new = []
        for location in possible_locations:
            distance = self.get_distance_difference(station_1=self.position, station_2=location)
            distances_new.append(distance)
            distance_old = self.get_distance_difference(station_1=chosen_node[0], station_2=location)
            distances_original.append(distance_old)
        average_old = np.average(np.array(distances_original))
        average_new = np.average(np.array(distances_new))
        delta = average_old - average_new
        # Values are in the magnitude of 10
        return delta

    def RL_Backprop(self, move_made, reward_multiplier, alpha, gamma, seekers, possible_locations):
        """
        Do the backpropagation for the Reinforcement Learning algorithm
        :param move_made: seeker's last move
        :param reward_multiplier: reward multiplier for the reward equation
        :param alpha: alpha for the Q-value update function
        :param gamma: gamma for the Q-value update function
        :param seekers: list of seekers
        :param possible_locations: list of possible locations of the player
        """
        # Based on total coverage achieved
        # Based on avoiding safe locations
        # Based on location categorisation

        # Get the original visit count and update it (used for coverage based reward)
        original_average_coverage = self.total_coverage(seekers=seekers)
        self.Update_visit_count(position=move_made[1], Visits=self.real_visits)
        new_coverage = self.get_real_coverage()
        self.real_coverage = new_coverage  # Update the real coverage
        new_average_coverage = self.total_coverage(seekers=seekers)

        # reward = reward_multiplier * (new_average_coverage - original_average_coverage)  # multiplier should be in the order of 100
        # reward = reward_multiplier * self.loc_cat_reward(categories=loc_cat)  # multiplier should be in the order of 1
        reward = reward_multiplier * self.avoid_area_reward(possible_locations=possible_locations, chosen_node=move_made) # multiplier should be in the order of 1/10

        nodes = self.generate_nodes(station_list=[self.position])
        future_q_values = self.generate_node_scores(node_list=nodes, Q_values=self.q_values)
        current_value = self.get_Q_value(node=move_made, Q_values=self.q_values)
        updated_value = self.Q_value_update(current_value=current_value, alpha=alpha, gamma=gamma, reward=reward,
                                            list_values=future_q_values)
        new_identity = [move_made[0], move_made[1], move_made[2], updated_value]
        self.Update_Q_value_list(new_value=new_identity)
