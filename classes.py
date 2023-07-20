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

    def minimise_distance(self, destination, Info=Info, exclude=None):
        """
        FInd the optmum station to move to to close distance between current location and a target
        :param destination: destination station
        :param Info: List containing map info
        :return: Station to move to
        """
        loc_destination = (0, 0)
        possible_station = []
        possible_x = []
        possible_y = []
        ticket_list = []
        if exclude is not None:
            excluded_stations = exclude
        else:
            excluded_stations = []
        for i in range(len(Info)):
            if Info[i][0] == destination:
                loc_destination = Info[i][1]
            if self.can_move(destination=Info[i][0], ticket=0) and Info[i][0] not in excluded_stations:
                possible_station.append(Info[i][0])
                possible_x.append(Info[i][1][0])
                possible_y.append(Info[i][1][1])
                ticket_list.append(0)
            if self.can_move(destination=Info[i][0], ticket=1) and Info[i][0] not in excluded_stations:
                possible_station.append(Info[i][0])
                possible_x.append(Info[i][1][0])
                possible_y.append(Info[i][1][1])
                ticket_list.append(1)
            if self.can_move(destination=Info[i][0], ticket=2) and Info[i][0] not in excluded_stations:
                possible_station.append(Info[i][0])
                possible_x.append(Info[i][1][0])
                possible_y.append(Info[i][1][1])
                ticket_list.append(2)
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
        chosen = possible_station[np.argmax(difference)]
        ticket_used = ticket_list[np.argmax(difference)]
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

    def remove_leaf_nodes(self, exclusion_list):
        check_bus = False
        check_underground = False
        check_taxi = False
        bus_errors = 0
        underground_errors =0
        taxi_errors =0
        for connection in self.bus_connections:
            if connection == 0:
                check_bus = True
            elif connection in exclusion_list:
                bus_errors+=1
                print("bus",len(self.bus_connections), bus_errors)

        for connection in self.underground_connections:
            if connection == 0:
                check_underground = True
            elif connection in exclusion_list:
                underground_errors+=1
                print("under",len(self.underground_connections), underground_errors)

        for connection in self.taxi_connections:
            if connection == 0:
                check_taxi = True
            elif connection in exclusion_list:
                taxi_errors+=1
                print("taxi",len(self.taxi_connections), taxi_errors)

        if bus_errors == len(self.bus_connections):
            check_bus = True
        if underground_errors == len(self.underground_connections):
            check_underground = True
        if taxi_errors == len(self.taxi_connections):
            check_taxi = True

        if check_bus and check_taxi and check_underground:
            return True
        else:
            return False

    def MCTS(self, N, last_ticket, seeker_list, player):
        counter = 0
        nodes = self.generate_nodes(station_list=[self.position])  # List of nodes in the tree
        node_q_values = self.generate_node_scores(node_list=nodes)  # The q-values of all the nodes in the tree
        leaf_nodes = self.generate_nodes(station_list=[self.position]) # List of leaf nodes
        parents = []
        for node in nodes:
            if node[0] not in parents:
                parents.append(int(node[0]))

        sim_running = True
        run_backprop = True
        error_counter = 0
        while counter < N:
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
            chosen_node_index = np.argmax(np.array(node_scores))
            chosen_node = leaf_nodes[chosen_node_index]
            Dummy_seeker = copy.deepcopy(self)  # Create a dummy seeker to use for the simulation
            Dummy_seeker.position = chosen_node[1]
            Dummy_seeker.get_info()

            ## Expansion ##
            print("leaf", leaf_nodes)
            print("nodes", nodes)
            print("exclusion list", parents)
            print("Selected node:", chosen_node, Dummy_seeker.position)
            expanded_node, ticket_used = Dummy_seeker.minimise_distance(destination=possible_location, exclude=parents)
            if expanded_node!=0:
                new_node = [chosen_node[1], expanded_node, ticket_used]
                print("trying to add" , new_node)
            else:
                new_node = nodes[-1]



            if new_node not in nodes:
                new_node_q_value = self.generate_node_scores(node_list=[new_node])[0]
                nodes.append(new_node) # Add to the tree
                leaf_nodes.append(new_node) # Add to list of leaf nodes
                node_q_values.append(new_node_q_value)
                leaf_nodes.pop(chosen_node_index) # Remove from leaf node so the UCT can not run on the parent node
                if new_node[0] not in parents:
                    parents.append(new_node[0])
                print("node added", new_node)
                error_counter = 0

            else:
                sim_running = False
                print("No unique nodes can be added")
                run_backprop = False
                error_counter += 1
                print(self.remove_leaf_nodes(exclusion_list=parents))
                if chosen_node[1] in parents or Dummy_seeker.remove_leaf_nodes(exclusion_list=parents):
                    leaf_nodes.pop(chosen_node_index)
                    print("Removed node from leaf node", chosen_node)



            ## Simulation ##

            Dummy_seeker.move(destination=expanded_node, ticket=ticket_used)
            while sim_running:
                player_target, player_ticket = Dummy_player.maximise_distance(Dummy_seeker.position)
                Dummy_player.move(destination=player_target, ticket=player_ticket)
                dummy_target, dummy_ticket = Dummy_seeker.minimise_distance(destination=player_target)
                if dummy_target != 0:
                    Dummy_seeker.move(destination=dummy_target, ticket=dummy_ticket)
                    Dummy_player.tickets[dummy_ticket] += 1
                else:
                    sim_running = False
                if Dummy_player.caught(Dummy_seeker) or np.sum(np.array(Dummy_seeker.tickets)) == 0 or np.sum(
                        np.array(Dummy_player.tickets)) == 0:
                    sim_running = False
            print("Simulation done")

            ## Backpropagation ##
            if run_backprop:
                if Dummy_player.caught(Dummy_seeker):
                    reward = 1
                else:
                    reward = -1
                node_path = [leaf_nodes[-1]]  # Get the path followed by the tree
                node_path_index = [-1]  # Create a list of the indexes of the Q_values to be updated
                last_node = node_path[-1]
                while last_node[0] != nodes[0][0]:  ## Fill the list until the last node in node path is the root node
                    for i in range(len(nodes)):
                        if last_node[0] == nodes[i][1]:
                            node_path.append(nodes[i])
                            node_path_index.append(i)
                    last_node = node_path[-1]
                    print(last_node)


                for i in range(len(node_path_index)):
                    index = node_path_index[i]
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

            print("End iteration", len(leaf_nodes))
            if error_counter < 5 and len(leaf_nodes) >0:
                counter += 1

            else:
                print("Total iterations done", counter+1)
                print("parents", len(parents))
                counter = N+1


        return nodes


alpha = 0.1
gamma = 0.2
X = Player("player", 189, [4, 8, 10])
S1 = Player("seeker", 120, [4, 8, 10])
S2 = Player("seeker", 121, [4, 8, 10])
S3 = Player("seeker", 193, [4, 8, 10])
Seekers = [S1, S2, S3]
S1_tickets = [4, 8, 10]
print(S1.MCTS(N=100, last_ticket=2, seeker_list=[S1, S2, S3], player=X))
