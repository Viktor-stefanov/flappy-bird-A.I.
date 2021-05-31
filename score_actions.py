import os

def update_high_score(new_high_score: str):
    with open("high_score.txt", "w") as hs:
        hs.write(new_high_score)

def get_high_score() -> int:
    # if the high_score file exists read from it
    if os.path.exists("high_score.txt"):
        with open("high_score.txt") as hs:
            hs = hs.readline()
    else: # if it doesn't create it
        update_high_score("0")
        hs = 0
    return int(hs)