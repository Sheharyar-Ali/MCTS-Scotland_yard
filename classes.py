import numpy as np

from data_read import Info, Q_values, Visits
from functions import *
import copy


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

    def move(self, destination, ticket):
        """
        Move to target location. Updates the connections of the entity
        :param destination: Target station
        :param ticket: Ticket used to get to target station
        :return: N/A
        """
        if self.can_move(destination=destination, ticket=ticket):
            self.position = destination
            self.tickets[ticket] -= 1
            self.get_info()
            if self.position == "player":
                print("Player moved to station: ", self.position)
    def get_station_info(self, station, Info=Info):
        required = 0
        for stations in Info:
            if stations[0] == station:
                required = stations
        return required


    def get_remaining_nodes(self, station, node_list,exclusion_list):
        generated_nodes = self.generate_nodes(station_list=[station])
        to_remove=[]
        for node in generated_nodes:
            if node in node_list or node[1] in exclusion_list:
                to_remove.append(node)
        for node in to_remove:
            generated_nodes.remove(node)
        return generated_nodes

    def minimise_distance(self, destination, node_list,  exclude_stations=None, node_exclusion_list=None):
        """
        FInd the optmum station to move to to close distance between current location and a target
        :param destination: destination station
        :param Info: List containing map info
        :return: Station to move to
        """
        if exclude_stations is not None:
            valid_nodes = self.get_remaining_nodes(station=self.position, node_list=node_list, exclusion_list=exclude_stations)
        else:
            valid_nodes = self.generate_nodes(station_list=[self.position])

        destination_station= self.get_station_info(station=destination)
        loc_destination = destination_station[1]
        possible_station = []
        possible_x = []
        possible_y = []
        ticket_list = []
        for node in valid_nodes:
            if self.can_move(destination=node[1], ticket=node[2]):
                station_info = self.get_station_info(node[1])
                possible_x.append(station_info[1][0])
                possible_y.append(station_info[1][1])
                ticket_list.append(node[2])
                possible_station.append(node[1])



        #
        # if exclude_stations is not None:
        #     excluded_stations = exclude_stations
        # else:
        #     excluded_stations = []
        # if node_exclusion_list is None:
        #     node_exclusion_list = []
        # for i in range(len(Info)):
        #     if Info[i][0] == destination:
        #         loc_destination = Info[i][1]
        #     for ticket in tickets_to_use:
        #         exclusion_check = [Info[i][0], ticket]
        #         if self.can_move(destination=Info[i][0], ticket=ticket) and Info[i][
        #             0] not in excluded_stations and exclusion_check not in node_exclusion_list:
        #             possible_station.append(Info[i][0])
        #             possible_x.append(Info[i][1][0])
        #             possible_y.append(Info[i][1][1])
        #             ticket_list.append(ticket)
        possible_x = np.array(possible_x)
        possible_y = np.array(possible_y)
        difference = np.sqrt(abs(possible_x - loc_destination[0]) ** 2 + abs(possible_y - loc_destination[1]) ** 2)
        if len(difference) != 0:
            chosen = possible_station[np.argmin(difference)]
            ticket_used = ticket_list[np.argmin(difference)]

        else:
            print("No legal move for minimise distance function")
            chosen = 0
            ticket_used = 0

        return chosen, ticket_used

    def maximise_distance(self, target, Info=Info):
        """
        Find the optimum station to move to, to maximise distance between you and a target station
        :param target: Station you want to move the furthest away from
        :param Info: List containing map info
        :return: Station to move to
        """
        loc_target = (0, 0)
        possible_station = []
        possible_x = []
        possible_y = []
        ticket_list = []
        for i in range(len(Info)):
            if Info[i][0] == target:
                loc_target = Info[i][1]
            if self.can_move(destination=Info[i][0], ticket=0):
                possible_station.append(Info[i][0])
                possible_x.append(Info[i][1][0])
                possible_y.append(Info[i][1][1])
                ticket_list.append(0)
            if self.can_move(destination=Info[i][0], ticket=1):
                possible_station.append(Info[i][0])
                possible_x.append(Info[i][1][0])
                possible_y.append(Info[i][1][1])
                ticket_list.append(1)
            if self.can_move(destination=Info[i][0], ticket=2):
                possible_station.append(Info[i][0])
                possible_x.append(Info[i][1][0])
                possible_y.append(Info[i][1][1])
                ticket_list.append(2)
        possible_x = np.array(possible_x)
        possible_y = np.array(possible_y)
        difference = np.sqrt(abs(possible_x - loc_target[0]) ** 2 + abs(possible_y - loc_target[1]) ** 2)
        if len(difference) != 0:
            chosen = possible_station[np.argmax(difference)]
            ticket_used = ticket_list[np.argmax(difference)]
        else:
            chosen = 0
            ticket_used = 0
        return chosen, ticket_used

    def UCT(self, parent, child, transport, Q_values=Q_values, Visits=Visits):
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
        C = 0.5
        W = 5
        x_a = np.average(scores)
        V = x_i + (C * np.sqrt(np.log(n_p) / n_i)) + (W * (x_a / (n_i * (1 - x_i) + 1)))

        return V

    def generate_nodes(self, station_list, Info=Info):
        """
        Generate a list of possible nodes from the required station. This is used in the MCTS
        :param station_list: List of stations from which to generate the nodes
        :param Info: Information about the stations
        :return: List containing the nodes in the format [[origin_1, destination_1, ticket_used_1], ..., [origin_i, destination_i, ticket_used_i]]
        """
        nodes = []
        for i in range(len(station_list)):
            station = station_list[i]
            for j in range(len(Info)):
                if Info[j][0] == station and Info[j][2] != [0]:
                    for k in range(len(Info[j][2])):
                        nodes.append([station, Info[j][2][k], 0])
                if Info[j][0] == station and Info[j][3] != [0]:
                    for k in range(len(Info[j][3])):
                        nodes.append([station, Info[j][3][k], 1])
                if Info[j][0] == station and Info[j][4] != [0]:
                    for k in range(len(Info[j][4])):
                        nodes.append([station, Info[j][4][k], 2])

        return nodes

    def generate_node_scores(self, node_list, Q_values=Q_values):
        node_scores = []
        for i in range(len(node_list)):
            node = node_list[i]
            for j in range(len(Q_values)):
                if Q_values[j][0] == node[0] and Q_values[j][1] == node[1] and Q_values[j][2] == node[2]:
                    node_scores.append(Q_values[j][3])

        return node_scores

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



    def generate_node_exclusion_list(self, station, node_list):
        valid_nodes = self.generate_nodes(station_list=[station])
        exclusion_list = []
        for node in valid_nodes:
            if node in node_list:
                exclusion_list.append([node[1], node[2]])

        return exclusion_list

    def MCTS(self, N, last_ticket, seeker_list, player):
        counter = 0
        nodes = self.generate_nodes(station_list=[self.position])  # List of nodes in the tree
        node_q_values = self.generate_node_scores(node_list=nodes)  # The q-values of all the nodes in the tree
        leaf_nodes = self.generate_nodes(station_list=[self.position])  # List of leaf nodes
        exclusion_list = [int(nodes[0][0])]
        path_list_indexed, path_index, path_list = self.generate_path(node_list=nodes)

        error_counter = 0
        while counter < N:
            sim_running = True
            run_backprop = True
            ## Initialise ##
            node_scores = []  # The scores of all the leaf nodes in the tree (For Selection)
            possible_location = location_hider(Info=Info, ticket=last_ticket, seekers=seeker_list)
            Dummy_player = copy.deepcopy(player)  # Create a Dummy player to use for the simulation
            Dummy_player.position = possible_location
            Dummy_player.get_info()

            ## Selection ##

            for node in leaf_nodes:
                v_i = self.UCT(node[0], node[1], node[2])
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
            print("leaf", leaf_nodes)
            print("nodes", nodes)
            print("Selected node:", chosen_node, Dummy_seeker.position)
            expanded_node, ticket_used = Dummy_seeker.minimise_distance(destination=possible_location,
                                                                        exclude_stations=exclusion_list,
                                                                        node_list=nodes)

            new_node = [chosen_node[1], expanded_node, ticket_used]
            print("trying to add:", new_node)

            if expanded_node == 0:
                new_node = nodes[-1]


            print("exclusion list", exclusion_list)
            if new_node not in nodes:
                new_node_q_value = self.generate_node_scores(node_list=[new_node])[0]
                nodes.append(new_node)  # Add to the tree
                leaf_nodes.append(new_node)  # Add to list of leaf nodes
                node_q_values.append(new_node_q_value)
                leaf_nodes.pop(chosen_node_index)  # Remove from leaf node so the UCT can not run on the parent node
                check_full_connections = self.all_full_connections(station=new_node[0],
                                                                   node_list=nodes)  # See if this node has any more connections left to explore
                if check_full_connections:
                    exclusion_list.append(new_node[0])
                print("node added", new_node)
                error_counter = 0

            else:
                sim_running = False
                print("No unique nodes can be added")
                run_backprop = False
                error_counter += 1

            ## Simulation ##

            Dummy_seeker.move(destination=expanded_node, ticket=ticket_used)
            while sim_running:
                player_target, player_ticket = Dummy_player.maximise_distance(Dummy_seeker.position)
                if player_target != 0:
                    Dummy_player.move(destination=player_target, ticket=player_ticket)
                dummy_target, dummy_ticket = Dummy_seeker.minimise_distance(destination=Dummy_player.position, node_list=nodes)
                if dummy_target != 0:
                    Dummy_seeker.move(destination=dummy_target, ticket=dummy_ticket)
                    Dummy_player.tickets[dummy_ticket] += 1
                else:
                    sim_running = False
                if Dummy_player.caught(Dummy_seeker) or np.sum(np.array(Dummy_seeker.tickets)) == 0:
                    sim_running = False
                    if Dummy_player.caught(Dummy_seeker):
                        print("SIM ENDED BECAUSE MR X CAUGHT")
            print("Simulation done")
            Dummy_seeker.tickets = self.tickets

            ## Backpropagation ##
            if run_backprop:
                if Dummy_player.caught(Dummy_seeker):
                    reward = 1
                else:
                    reward = 0
                node_path_index = path_index[chosen_node_index_full]
                path_index.append(node_path_index)
                node_path = path_list_indexed[node_path_index]  # Add the new node destination to the appropriate path
                node_path.append(chosen_node_index_full)
                path_list_indexed[node_path_index] = node_path
                path_list[node_path_index].append(new_node[1])

                for i in range(len(node_path)):
                    index = node_path[i]
                    current_value = node_q_values[index]
                    list_future_values = node_q_values[0:i]
                    updated_value = Q_value_update(current_value=current_value, alpha=alpha, gamma=gamma, reward=reward,
                                                   list_values=list_future_values)
                    node_q_values[index] = updated_value
                    new_identity = [nodes[index][0], nodes[index][1], nodes[index][2], updated_value]
                    check = Update_Q_value_list(new_value=new_identity, Q_values=Q_values)

                    if i == 0:

                        check_2 = Update_visit_count(position=nodes[index][0], Visits=Visits)

                        check_3 = Update_visit_count(position=nodes[index][1], Visits=Visits)
                    else:
                        check_2 = Update_visit_count(position=nodes[index][0], Visits=Visits)

            ## Remove fully explored nodes from leaf node list
            for check_node in leaf_nodes:
                print("End check")
                remaining_nodes = self.get_remaining_nodes(station=check_node[1], node_list=nodes, exclusion_list=exclusion_list)
                print("Remaining nodes for ", check_node, remaining_nodes, exclusion_list)
                if self.all_full_connections(station=check_node[1], node_list=nodes):
                    print("Removing at end of iteration: ", check_node)
                    leaf_nodes.remove(check_node)
                elif len(remaining_nodes) == 0:
                    print("Removing at end of iteration: ", check_node,remaining_nodes)
                    leaf_nodes.remove(check_node)


            exclusion_list.pop(-1)  # remove origin from the excluded list
            print("End iteration", counter)
            # print("path list",path_list)
            if error_counter < 5 and len(leaf_nodes) > 0:
                counter += 1

            else:
                print("Total iterations done", counter + 1)
                print("parents", len(exclusion_list))
                counter = N + 1


        parent = self.position
        values = []
        values_index=[]
        for i in range(len(nodes)):
            node = nodes[i]
            if node[0] == parent:
                values.append(get_Q_value(node=node,Q_values=Q_values))
                values_index.append(i)
        values=np.array(values)
        Best_index = values_index[np.argmax(values)]
        Best_move = nodes[Best_index]



        return Best_move, node_q_values[Best_index], node_q_values


alpha = 0.1
gamma = 0.2
X = Player("player", 189, [4, 8, 10])
S1 = Player("seeker", 120, [4, 8, 10])
S2 = Player("seeker", 121, [4, 8, 10])
S3 = Player("seeker", 193, [4, 8, 10])
Seekers = [S1, S2, S3]
S1_tickets = [4, 8, 10]
print(S1.MCTS(N=1000, last_ticket=2, seeker_list=[S1, S2, S3], player=X))
