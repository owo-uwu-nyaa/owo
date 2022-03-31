import random
import re
from owobot.misc import uwu_data

_DO_NOT_OWOFY = r"(http.*)|(<.*>)"

"""
wwhat the fuck even is owo/uwu

some definitions: https://github.com/Daniel-Liu-c0deb0t/uwu
and https://github.com/FernOfSigma/owoifier/blob/main/owoifier/owoifier.py
these seem to be important modifications as in https://github.com/FernOfSigma/owoifier/blob/main/owoifier/owoifier.py:
- replace r/l with w
- map some words to other word; e.g. cute -> kawaii~, na -> nya
- add *creepyasterisks* suffix/prefix, e.g. rawr x3, nuzzles etc.
- stutter
- context based replacements: add *cwute* stars,
"""


def score(text: str) -> float:
    text = re.sub(_DO_NOT_OWOFY, " ", text).lower()
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
        nmsg.append(random.choice(uwu_data.prefixes) + ' ')
    # returns list of words alternating with whitespace (in this order, word may be empty)
    split = re.split(r"(\s+)", text)
    is_seperator = True
    for word in split:
        is_seperator = not is_seperator
        if is_seperator or word == "" or re.match(_DO_NOT_OWOFY, word):
            nmsg.append(word)
            continue
        for mapping in uwu_data.mappings:
            word = word.replace(mapping[0], mapping[1])
        if random.randint(0, 10) > 8 and word[0].isalpha():
            word = f"{word[0]}-{word[0]}-{word}"

        nmsg.append(word)
        if word[-1] in [".", ",", "?"]:
            nmsg.append(' ' + random.choice(uwu_data.int_emote))
    return "".join(nmsg)


def get_random_emote() -> str:
    return random.choice(uwu_data.int_emote)


def get_random_sorry() -> str:
    return random.choice(uwu_data.sowwy)
