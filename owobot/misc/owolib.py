import random
from owobot.misc import uwu_data

"""
wwhat the fuck even is owo/uwu

some definitions: https://github.com/Daniel-Liu-c0deb0t/uwu and https://github.com/FernOfSigma/owoifier/blob/main/owoifier/owoifier.py
these seem to be important modifications as in https://github.com/FernOfSigma/owoifier/blob/main/owoifier/owoifier.py:
- replace r/l with w
- map some words to other word; e.g. cute -> kawaii~, na -> nya
- add *creepyasterisks* suffix/prefix, e.g. rawr x3, nuzzles etc.
- stutter
- context based replacements: add *cwute* stars,

"""


def score(msg: str) -> float:
    msg = msg.lower()
    spirit_count = 0
    for spirit in uwu_data.good_owo_spirit:
        if spirit in msg:
            spirit_count += 1
    map_count = 0
    lost_owo_potential = 0
    for mapping in uwu_data.mappings[2:]:
        if mapping[1] in msg:
            map_count += 1
        if mapping[0] in msg:
            lost_owo_potential += 1
    return (map_count * 15 + spirit_count * 10 - (lost_owo_potential * 4)) / len(msg)


def owofy(msg: str) -> str:
    # con: not that efficient
    # pro: works
    for map in uwu_data.mappings:
        msg = msg.replace(map[0], map[1])
    nmsg = []
    if random.randint(0, 10) > 7:
        nmsg.append(random.choice(uwu_data.prefixes))
    for word in str.split(msg):
        if random.randint(0, 10) > 8 and word[0].isalpha():
            nmsg.append(f"{word[0]}-{word[0]}-{word}")
        else:
            nmsg.append(word)
        if word[-1] in [".", ",", "?"]:
            nmsg.append(random.choice(uwu_data.int_emote))
    return " ".join(nmsg)


def get_random_emote() -> str:
    return random.choice(uwu_data.int_emote)


def get_random_sorry() -> str:
    return random.choice(uwu_data.sowwy)