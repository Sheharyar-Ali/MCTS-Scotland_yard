import numpy as np


def weighted_selection(cat_1, cat_2, cat_3, p1, p2, p3):
    """
    Uses the probabilities to perform a weighted selection and returns a possible location of the player

    :param cat_1: list of stations in category 1
    :param cat_2: list of stations in category 2
    :param cat_3: list of stations in category 3
    :param p1: probability of player choosing a cat_1 station
    :param p2: probability of player choosing a cat_2 station
    :param p3: probability of player choosing a cat_3 station
    :return: Station where the player could be
    """
    list = np.arange(0, 11, 1)
    P1 = int(p1 * 10)
    P2 = int(p2 * 10)
    P3 = int(p3 * 10)
    l1 = list[0:P1]
    l2 = list[P1: P2 + P1]
    l3 = list[P2 + P1: P1 + P2 + P3]
    number = np.random.randint(0, 10)
    if number in l1:
        chosen = cat_1[np.random.randint(0, len(cat_1))]
    elif number in l2:
        chosen = cat_2[np.random.randint(0, len(cat_2))]
    else:
        chosen = cat_3[np.random.randint(0, len(cat_3))]

    return chosen


def location_hider(Info, player, seekers):
    """
    Compiles a list of all possible locations that the player can be on. These are split into 3 categories and a
    weighted selection is performed to determine one station where the player can be.
    :param Info: list of all stations and their connections
    :param player: the Player class
    :param seekers: List of seekers
    :return: Possible location of Player
    """
    loc_seekers = []
    cat_1 = []  # Only taxis
    cat_2 = []  # bus + taxi
    cat_3 = []  # underground + taxi + bus
    for i in range(len(seekers)):
        loc_seekers.append(seekers[i].position)
    tickets = player.tickets
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
                if (target in bus_con and tickets[0] > 0) or (target in underground_con and tickets[1] > 0) or (
                        target in taxi_con and tickets[2] > 0):
                    check = True
                if check and target not in possible_locations and target not in loc_seekers:
                    possible_locations.append(target)

    location = weighted_selection(cat_1, cat_2, cat_3, 0.3, 0.3, 0.4)

    return location
