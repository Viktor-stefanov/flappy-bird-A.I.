def update_high_score(new_high_score: str):
    with open("high_score.txt", "w") as hs:
        hs.write(new_high_score)

def get_high_score() -> int:
    with open("high_score.txt") as hs:
        hs = hs.readline()
    return int(hs)