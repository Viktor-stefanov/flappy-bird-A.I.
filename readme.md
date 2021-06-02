# Flappy Bird Clone

## Requirements:
python3+, pygame, neat-python

## Controls:
#### A.I. playing the game:

D - TOGGLE THE A.I.'s VISION
R - RESET THE CURRENT GENERATIONS AND START A NEW ONE
K - KILL THE CURRENT GENERATION

#### Player-controled game:

SPACEBAR / LEFT CLICK - JUMP
R / ENTER - RESTART (in the respawn menu)

#### Mutual keybinds

Q / ESCAPE - CLOSE GAME
M - MAIN MENU

## Instructions
If you want to tinker around with the fitness function (ai_play_game line: 305) I have left usefull comments
to guide you and tell you what to do. You can change the number of inputs from 3 to 2 (just uncomment & replace variable names),
you can mess with the inputs if you wish to. To make any changes to the A.I. behaviour outside the fitness function
(activation function, mutate rate, add note rate, population size...) you have to change the config file.
