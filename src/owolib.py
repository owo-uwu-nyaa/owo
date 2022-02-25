import random
import uwu_data

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
    owo_chars = 0
    for c in uwu_data.owo_chars:
        owo_chars += msg.count(c)
    emo_count = 0
    for emo in uwu_data.int_emote:
        if emo in msg:
            emo_count += 1
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
    return (owo_chars * 3 + map_count * 10 + spirit_count * 10 - (lost_owo_potential * 4)) / len(msg)


def owofy(msg: str) -> str:
    # con: not that efficient
    # pro: works
    for map in uwu_data.mappings:
        msg = msg.replace(map[0], map[1])
    nmsg = []
    if random.randint(0, 10) > 7:
        nmsg.append(random.choice(uwu_data.prefixes))
    words = str.split(msg)
    for word in words:
        if random.randint(0, 10) > 8 and word[0].isalpha():
            nmsg.append(f"{word[0]}-{word[0]}-{word}")
        else:
            nmsg.append(word)
        if word[-1] in [".", ",", "?"]:
            nmsg.append(random.choice(uwu_data.int_emote))
    return " ".join(nmsg)
