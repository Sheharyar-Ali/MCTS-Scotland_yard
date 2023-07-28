from classes import *

## Initialise ##

running = True
Round = 1
Round_limit = 24
Reveal_Rounds = [3, 8, 13, 18, 24] # [3, 6, 9, 12]
start_locations = randomise_start_locations(Info=Info, number_seekers=4)

X = Player("player", start_locations[0], [3, 3, 4])
S1 = Player("seeker", start_locations[1], [8, 4, 10])
S2 = Player("seeker", start_locations[2], [8, 4, 10])
S3 = Player("seeker", start_locations[3], [8, 4, 10])
S4 = Player("seeker", start_locations[4], [8, 4, 10])
Seekers = [S1, S2, S3, S4]

normal_reward_multiplier = 10 # The reward multiplier for normal rounds
reveal_reward_multipler_MCTS = 1 # The reward multiplier used in the backpropagation of the MCTS in the reveal round
reveal_reward_multiplier_Rl = 1 # The reward multiplier used in the backpropagation of the RL in the reveal round
alpha_normal = 0.1  # "A study on automatic playing of Scotland Yard with RL and MCTS" (2018) by Cheng Qi and Chunyan Miao.
gamma_normal = 0.9  # "A study on automatic playing of Scotland Yard with RL and MCTS" (2018) by Cheng Qi and Chunyan Miao.
alpha_reveal = 0.1  # alpha for reveal rounds
gamma_reveal = 0.9  # gamma for reveal rounds
C_normal = 0.6
W_normal = 50
C_reveal = 0.1 # More exploitation and less exploration
W_reveal = 50

print("Seeker starting locations: Seeker 1: ", S1.position, "Seeker 2:", S2.position, "Seeker 3:", S3.position, "Seeker 4: ", S4.position)
while running:
    ## Player's turn ##
    print("Round", Round, "out of ", Round_limit)
    if Round in Reveal_Rounds:
        print("BE CAREFUL, SEEKERS WILL KNOW YOUR POSITION AFTER THIS MOVE")
    print("Your current location is: ", X.position)
    print("You have the following tickets available: Bus", X.tickets[0], "Underground", X.tickets[1], "Taxi",
          X.tickets[2])
    possible_moves = X.generate_nodes(station_list=[X.position])
    for i in range(len(possible_moves)):
        move = possible_moves[i]
        print(" Choice ", i + 1, "Move to station: ", move[1], " using", Ticket(move[2]).name)
    chosen_move = 123
    while chosen_move > len(possible_moves) or chosen_move < 0:
        chosen_move = int(input("Please indicate which move you want to make"))
    move = possible_moves[chosen_move - 1]
    X.move(destination=move[1], ticket=move[2])

    ## Seekers' turn ##
    if Round not in Reveal_Rounds:
        ticket_used = move[2]
        for i in range(len(Seekers)):
            seeker = Seekers[i]
            if sum(np.array(seeker.tickets)) > 0:
                seeker_move = seeker.MCTS(N=1000, last_ticket=ticket_used, seeker_list=Seekers, player=X, seekers=Seekers, C=C_normal, W=W_normal, alpha=alpha_normal, gamma=gamma_normal)
                seeker.move(destination=seeker_move[1], ticket=seeker_move[2], print_warning=True)
                print("Seeker", i + 1, "moved to", seeker.position, "using ", Ticket(seeker_move[2]).name, seeker.tickets)
                X.tickets[seeker_move[2]] += 1
                if seeker.caught(other_player=X):
                    running = False
                    print("Seeker", i + 1, "has caught Mr X!!!")
                seeker.RL_Backprop(move_made=seeker_move, reward_multiplier=normal_reward_multiplier, alpha=alpha_normal, gamma=gamma_normal)
            else:
                print("Seeker ", i+1, "out of tickets. Position is ", seeker.position)

    else:
        print("Reveal round so seekers know your current location")
        ticket_used = move[2]
        possible_locations = Arrange_seekers(seeker_list=Seekers,player=X)
        for i in range(len(Seekers)):
            seeker = Seekers[i]
            if sum(np.array(seeker.tickets)) > 0:
                seeker_move = seeker.MCTS_reveal_round(N=1000, possible_location=possible_locations[i], player=X, seekers=Seekers, C=C_reveal, W=W_reveal, alpha=alpha_reveal, gamma=gamma_reveal,reward_multiplier=reveal_reward_multipler_MCTS)
                seeker.move(destination=seeker_move[1], ticket=seeker_move[2], print_warning=True)
                print("Seeker", i + 1, "moved to", seeker.position, "using ", Ticket(seeker_move[2]).name)
                X.tickets[seeker_move[2]] += 1
                if seeker.caught(other_player=X):
                    running = False
                    print("Seeker", i + 1, "has caught Mr X!!!")
                seeker.RL_Backprop(move_made=seeker_move, reward_multiplier=reveal_reward_multiplier_Rl, alpha=alpha_normal, gamma=gamma_normal)
            else:
                print("Seeker ", i+1, "out of tickets. Position is ", seeker.position)

    Round += 1
    print("#########")
    if Round > Round_limit:
        running = False
for seeker in Seekers:
    seeker.get_coverage(visit_count=seeker.visits)
    print(seeker.coverage)