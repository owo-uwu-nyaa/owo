import random
import re

from misc import uwu_data

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

_do_not_owofy = r"http*.|<*.>"

def score(text: str) -> float:
    text = re.sub(_do_not_owofy, " ", text).lower()
    spirit_count = 0
    for spirit in uwu_data.good_owo_spirit:
        if spirit in text:
            spirit_count += 1
    map_count = 0
    lost_owo_potential = 0
    for mapping in uwu_data.mappings:
        if mapping[1] in text:
            map_count += 1
        if mapping[0] in text:
            lost_owo_potential += 1
    stuttewing = 0
    for word in text.split():
        stuttewing += word.count("-")
    return (stuttewing * 20 + map_count * 15 + spirit_count * 10 - lost_owo_potential) / len(text)


def owofy(text: str) -> str:
    # con: not that efficient
    # pro: works
    nmsg = []
    if random.randint(0, 10) > 7:
        nmsg.append(random.choice(uwu_data.prefixes))
    for word in str.split(text):
        if re.match(_do_not_owofy, word):
            nmsg.append(word)
            continue
        for map in uwu_data.mappings:
            word = word.replace(map[0], map[1])
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
