# Using Reinforcement Learning to Play Scotland Yard #

This project is all about using Reinforcement Learning to play Scotland Yard against a human player. This is a project for AE4350 Bio-Inspired Learning and Intelligence for Aerospace Systems.


## How to play ##
The game can be started by running the `main.py` file. The file contains a range of settings that can be changed in case you want to make the game longer or shorter.

You play as the elusive Mr. X and your job is to evade the seekers for 24 rounds in a small part of London. To do this you will be using tickets to travel around the map and skillfully avoid the 4 seekers trying to hunt you down.

1. When the game starts, you will see a map where your position is circled in Green. The seekers are circled in Red
2. The console shows you what moves you can make from this particular location and you choose your move by entering the number of the move you want to make
3. Stations connected with a blue line are **bus stations** and stations connected with a dotted red line are **underground stations**. You only have a limited number of tickets for these stations so be sure to select your moves carefully.
4. After every move, the seekers will try to predict where you are and will move to try and capture you.
5. The seekers' locations are always visible on your map.
6. Every time a seeker uses a ticket, that ticket gets added to your supply of tickets
7. Every so often, a **Reveal Round** will happen. **BE CAREFUL** because the seekers will know your exact location after this move so choose wisely!
8. The game ends if you are captured or after 24 Rounds.

**If you have trouble seeing the map properly, a high definition image is located in the `Images` folder**
