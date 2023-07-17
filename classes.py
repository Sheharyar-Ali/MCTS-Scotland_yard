from data_read import Info
from functions import *

class Ticket:
    def __init__(self, type):
        self.type = type  # int


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

    def get_info(self):
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
        elif self.tickets[ticket]<=0 and print_warning:
            print("Insufficient tickets for this move")
        elif print_warning:
            print("Can not move to new station from current station")

        return False

    def contact(self, other_player):
        if self.position == other_player.position:
            return True
        return False

    def move_player(self,destination,ticket):
        if self.can_move(destination=destination, ticket=ticket):
            self.position = destination
            self.tickets[ticket] -= 1
            self.get_info()
            print("Player moved to station: ", self.position)

    def minimise_distance(self, destination, Info=Info):
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
        for i in range(len(Info)):
            if Info[i][0] == destination:
                loc_destination = Info[i][1]
            if self.can_move(destination=Info[i][0], ticket=0):
                possible_station.append(Info[i][0])
                possible_x.append(Info[i][1][0])
                possible_y.append(Info[i][1][1])
            if self.can_move(destination=Info[i][0], ticket=1):
                possible_station.append(Info[i][0])
                possible_x.append(Info[i][1][0])
                possible_y.append(Info[i][1][1])
            if self.can_move(destination=Info[i][0], ticket=2):
                possible_station.append(Info[i][0])
                possible_x.append(Info[i][1][0])
                possible_y.append(Info[i][1][1])
        possible_x = np.array(possible_x)
        possible_y = np.array(possible_y)
        difference = np.sqrt(abs(possible_x - loc_destination[0]) ** 2 + abs(possible_y - loc_destination[1]) ** 2)
        chosen = possible_station[np.argmin(difference)]
        return chosen

    def maximise_distance(self, target, Info=Info):
        """
        Find the optimum station to move to to maximise distance between you and a target distance
        :param target: Station you want to move the furthest away from
        :param Info: List containing map info
        :return: Station to move to
        """
        loc_target = (0,0)
        possible_station = []
        possible_x = []
        possible_y = []
        for i in range(len(Info)):
            if Info[i][0] == target:
                loc_target = Info[i][1]
            if self.can_move(destination=Info[i][0], ticket=0):
                possible_station.append(Info[i][0])
                possible_x.append(Info[i][1][0])
                possible_y.append(Info[i][1][1])
            if self.can_move(destination=Info[i][0], ticket=1):
                possible_station.append(Info[i][0])
                possible_x.append(Info[i][1][0])
                possible_y.append(Info[i][1][1])
            if self.can_move(destination=Info[i][0], ticket=2):
                possible_station.append(Info[i][0])
                possible_x.append(Info[i][1][0])
                possible_y.append(Info[i][1][1])
        possible_x = np.array(possible_x)
        possible_y = np.array(possible_y)
        difference = np.sqrt(abs(possible_x - loc_target[0]) ** 2 + abs(possible_y - loc_target[1]) ** 2)
        chosen = possible_station[np.argmax(difference)]
        return chosen



X = Player("player", 189, [0, 0, 1])
S1 = Player("seeker", 163, [10,10,10])
S2 = Player("seeker", 192, [10,10,10])
S3 = Player("seeker", 193, [10,10,10])
Seekers = [S1, S2, S3]

check = location_hider(Info=Info, tickets=X.tickets, seekers=Seekers)
print(S1.maximise_distance(target=144))

