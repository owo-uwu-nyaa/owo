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


def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


def score(msg: str):
    l_count = msg.count('l')
    r_count = msg.count('r')
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

    score = 2 * ((((owo_chars * 1.5 + map_count * 5 + spirit_count * 5) - ((l_count  + r_count) * 0.5 + lost_owo_potential * 2)) * 5) / len(msg))
    return score


def owofy(msg: str):
    for map in uwu_data.mappings:
        msg = msg.replace(map[0], map[1])

    nmsg = ""
    words = str.split(msg)
    for word in words:
        if random.randint(0, 10) > 8 and word[0].isalpha():
            nmsg += f"{word[0]}-{word[0]}-{word} "
        else:
            nmsg += word + " "
    msg = nmsg

    # oh well this is going to be abused for sure
    # emotable_count = msg.count('.') + msg.count(',')
    nmsg = ""
    idxs = find(msg, '.')
    lastidx = 0
    for idx in idxs:
        nmsg += f"{msg[lastidx:idx]} {random.choice(uwu_data.int_emote)}"
        lastidx = idx
    if len(idxs) != 0:
        msg = nmsg + msg[idxs[-1]:]

    nmsg = ""
    lastidx = 0
    idxs = find(msg, ',')
    for idx in idxs:
        nmsg += f"{msg[lastidx:idx]} {random.choice(uwu_data.int_emote)}"
        lastidx = idx
    if len(idxs) != 0:
        msg = nmsg + msg[idxs[-1]:]

    lastidx = 0
    nmsg = ""
    idxs = find(msg, '?')
    for idx in idxs:
        nmsg += f"{msg[lastidx:idx]} {random.choice(uwu_data.int_emote)}"
        lastidx = idx
    if len(idxs) != 0:
        msg = nmsg + msg[idxs[-1]:]

    if random.randint(0, 10) > 7:
        msg = f'{random.choice(uwu_data.prefixes)} {msg}'
    msg = f'{msg}{random.choice(uwu_data.int_emote)}'
    return msg
