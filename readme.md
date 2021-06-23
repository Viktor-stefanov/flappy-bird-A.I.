# Flappy Bird & A.I.

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
If you want to tinker around with the fitness function (ai_play_game line: 305) I have left useful comments
to guide you and tell you what to do. You can change the number of inputs from 3 to 2 (just uncomment the variables, replace variables in the activation function call and change the # of inputs in the config file),
you can mess with the inputs or with the fitness gain/loss if you wish to. To make any changes to the A.I. behaviour outside the fitness function
(activation function, mutate rate, add note rate, population size...) you have to change the config file.
