from data_read import Info
from functions import location_hider

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

    def can_move(self, destination, ticket):
        if destination in self.connections[ticket] and self.tickets[ticket] > 0:
            return True
        elif self.tickets[ticket]<=0:
            print("Insufficient tickets for this move")
        else:
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




X = Player("player", 189, [0, 0, 1])
S1 = Player("seeker", 191, [10,10,10])
S2 = Player("seeker", 192, [10,10,10])
S3 = Player("seeker", 193, [10,10,10])
Seekers = [S1, S2, S3]

check = location_hider(Info=Info, player=X, seekers=Seekers)
print(check)
