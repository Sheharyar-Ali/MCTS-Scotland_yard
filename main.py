from classes import *
from graphics import *

## Initialise ##
comment = "Normal-coverage_reward"
running = True
caught = False
Round = 1
Round_limit = 24
Reveal_Rounds = [3, 8, 13, 18, 24]  # [3, 6, 9, 12]
Possible_locations_list = None  # Updated during reveal rounds
immobile_seeker = None
immobile_seeker_locations = []
max_location_search = 15
N = 1000

start_locations = randomise_start_locations(Info=Info, number_seekers=4)
X = Player("player", start_locations[0], [1, 1, 4])
S1 = Player("seeker", start_locations[1], [8, 4, 20])
S2 = Player("seeker", start_locations[2], [8, 4, 20])
S3 = Player("seeker", start_locations[3], [8, 4, 20])
S4 = Player("seeker", start_locations[4], [8, 4, 20])
# X = Player("player", 197, [8, 3, 3])
# S1 = Player("seeker", 153, [6, 4, 18])
# S2 = Player("seeker", 183, [6, 2, 20])
# S3 = Player("seeker", 184, [5, 3, 20])
# S4 = Player("seeker", 191, [5, 4, 19])
Seekers = [S1, S2, S3, S4]

Seekers_position = [S1.position, S2.position, S3.position, S4.position]
normal_reward_multiplier = 100  # The reward multiplier for normal rounds
reveal_reward_multiplier_Rl = 1  # The reward multiplier used in the backpropagation of the RL in the reveal round
alpha_normal = 0.1  # "A study on automatic playing of Scotland Yard with RL and MCTS" (2018) by Cheng Qi and Chunyan Miao. Make it more aggressive
gamma_normal = 0.9  # "A study on automatic playing of Scotland Yard with RL and MCTS" (2018) by Cheng Qi and Chunyan Miao.
alpha_reveal = 0.1  # alpha for reveal rounds
gamma_reveal = 0.9  # gamma for reveal rounds
C_normal = 0.2
W_normal = 50

# location = 197
# print(MCTS(seekers=Seekers, player=X, Round=Round, Round_limit=Round_limit,
#                                            possible_location=location, N=N,
#                                            C=C_normal, W=W_normal, r=0, alpha=alpha_normal, gamma=gamma_normal))
# exit()
print("Seeker starting locations: Seeker 1: ", S1.position, "Seeker 2:", S2.position, "Seeker 3:", S3.position,
      "Seeker 4: ", S4.position)

Draw_positions(player=X, seekers=Seekers, immobile_seeker_locations=immobile_seeker_locations)
while running:
    pg.display.flip()
    ## Player's turn ##
    print("Round", Round, "out of ", Round_limit)
    if Round in Reveal_Rounds:
        print("BE CAREFUL, SEEKERS WILL KNOW YOUR POSITION AFTER THIS MOVE")
    print("Your current location is: ", X.position)
    print("You have the following tickets available: Bus", X.tickets[0], "Underground", X.tickets[1], "Taxi",
          X.tickets[2])
    possible_moves = X.generate_nodes(station_list=[X.position])
    safe_moves = []
    # Filter out occupied mstations
    for i in range(len(possible_moves)):
        move = possible_moves[i]
        if move[1] not in Seekers_position and move[1] not in immobile_seeker_locations:
            safe_moves.append(move)
    # Ask player to make choice
    if len(safe_moves) == 0:
        print("No valid moves to make")
        running = False
        caught = True
    else:
        for i in range(len(safe_moves)):
            move = safe_moves[i]
            print(" Choice ", i + 1, "Move to station: ", move[1], " using", Ticket(move[2]).name)
        chosen_move = 123
        while chosen_move > len(safe_moves) or chosen_move < 0:
            chosen_move = int(input("Please indicate which move you want to make "))
        move = safe_moves[chosen_move - 1]
        X.move(destination=move[1], ticket=move[2])

    ## Seekers' turn ##
    if Round not in Reveal_Rounds and running:
        ticket_used = move[2]
        seeker_moves = []
        seeker_move_scores = []
        location_list_short = []
        Possible_locations_list = update_possible_location_list(possible_locations=Possible_locations_list, Info=Info,
                                                                seekers=Seekers,
                                                                ticket=ticket_used, player=X)
        X.update_loc_cat(player=X, location_list=Possible_locations_list)

        if len(Possible_locations_list) > max_location_search:
            N = 500
            while len(location_list_short) < max_location_search:
                chosen_location = location_hider(player=X, possible_locations=Possible_locations_list)
                if chosen_location not in location_list_short:
                    location_list_short.append(chosen_location)
                else:
                    Possible_locations_list.remove(chosen_location)
        else:
            location_list_short = Possible_locations_list
            N = 1000
        print("location list", location_list_short)
        for location in location_list_short:
            seeker_move, move_score = MCTS(seekers=Seekers, player=X, Round=Round, Round_limit=Round_limit,
                                           possible_location=location, N=N,
                                           C=C_normal, W=W_normal, r=0.2, alpha=alpha_normal, gamma=gamma_normal)
            seeker_moves.append(seeker_move)
            seeker_move_scores.append(move_score)
        print(seeker_moves)
        print(seeker_move_scores)
        move_chosen = seeker_moves[np.argmax(seeker_move_scores)]
        print("chosen location", location_list_short[np.argmax(seeker_move_scores)])
        for i in range(len(Seekers)):
            seeker = Seekers[i]
            if sum(np.array(seeker.tickets)) > 0:
                seeker_move = move_chosen[i]
                if seeker_move != [0, 0, 0]:
                    seeker.move(destination=seeker_move[1], ticket=seeker_move[2], print_warning=True)
                    print("Seeker", i + 1, "moved to", seeker.position, "from ", seeker_move[0], "using ",
                          Ticket(seeker_move[2]).name,
                          seeker.tickets)
                    X.tickets[seeker_move[2]] += 1
                    if seeker.caught(other_player=X):
                        running = False
                        print("Seeker", i + 1, "has caught Mr X!!!")
                        caught = True
                    seeker.RL_Backprop(move_made=seeker_move, reward_multiplier=normal_reward_multiplier,
                                       alpha=alpha_normal, gamma=gamma_normal, seekers=Seekers,
                                       possible_locations=location_list_short)
                else:
                    immobile_seeker = seeker
                    if seeker.position not in immobile_seeker_locations:
                        immobile_seeker_locations.append(seeker.position)
            else:
                print("Seeker ", i + 1, "out of tickets. Position is ", seeker.position)
            Seekers_position[i] = seeker.position

    elif running and Round in Reveal_Rounds:
        Possible_locations_list = [X.position]
        print("Reveal round so seekers know your current location")
        ticket_used = move[2]
        possible_locations_arranged = Arrange_seekers(seeker_list=Seekers, player=X)
        for i in range(len(Seekers)):
            seeker = Seekers[i]
            if sum(np.array(seeker.tickets)) > 0:
                seeker.Movement_Reveal_Round(possible_location=possible_locations_arranged[i], seekers=Seekers,
                                             player=X, alpha=alpha_reveal, gamma=gamma_reveal,
                                             reward_multiplier=reveal_reward_multiplier_Rl)
                if seeker.caught(other_player=X) or X.position in immobile_seeker_locations:
                    running = False
                    print("Seeker", i + 1, "has caught Mr X!!!")
                    caught = True
            else:
                print("Seeker ", i + 1, "out of tickets. Position is ", seeker.position)
            Seekers_position[i] = seeker.position

    Round += 1
    if immobile_seeker is not None:
        Seekers.remove(immobile_seeker)
        immobile_seeker = None
        print("Immobile Seeker removed")

    print("#########")
    Draw_positions(player=X, seekers=Seekers, immobile_seeker_locations=immobile_seeker_locations)

    if Round > Round_limit:
        running = False

print(loc_cat)
write_loc_cat_file("Location_categorisation.csv")
for seeker in Seekers:
    print(seeker.get_real_coverage())
coverage = [S1.get_real_coverage(), S2.get_real_coverage(), S3.get_real_coverage(), S4.get_real_coverage()]
coverage = np.array(coverage)
coverage = sum(coverage) / len(coverage)
print("Average Coverage", coverage)
Updated_q_values = update_centralised_q_values(seekers=Seekers, Q_values=Q_values)
write_q_file(file_name="q_values.csv", Q_values=Updated_q_values)
write_data_file(file_name="run_data.csv", alpha_normal=alpha_normal, gamma_normal=gamma_normal,
                alpha_reveal=alpha_reveal, gamma_reveal=gamma_reveal, C=C_normal, W=W_normal, Caught=caught,
                comments=comment, Rounds=Round - 1, coverage=coverage)
