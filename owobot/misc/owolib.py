import random
import re
from owobot.misc.common import discord_linkify_likely
from owobot.misc import uwu_data

from discord.utils import escape_markdown

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
    if not text:
        return 0
    text = re.sub(_DO_NOT_OWOFY, " ", text).lower()
    spirit_count = 0
    for spirit in uwu_data.good_owo_spirit:
        if spirit in text:
            spirit_count += 1
    map_count = 0
    lost_owo_potential = 0
    for before, _, after in uwu_data.mappings:
        if re.match(after, text):
            map_count += 1
        if re.match(before, text):
            lost_owo_potential += 1
    stuttewing = 0
    for word in text.split():
        stuttewing += word.count("-")
    return (
        stuttewing * 20 + map_count * 15 + spirit_count * 10 - lost_owo_potential
    ) / len(text)


def replace_non_overlapping(text, mappings):
    matches = []
    for (before, after) in mappings:
        replacer = after if callable(after) else lambda m: m.expand(after)
        for match in re.finditer(before, text):
            for other_match, _ in matches:
                # ranges overlap if x1 < y2 && y1 < x2
                if match.start() < other_match.end() and other_match.start() < match.end():
                    break
            else:  # no break
                matches.append((match, replacer(match)))
    matches = sorted(matches, key=lambda m: m[0].start())
    result = []
    prev_end = 0
    for match, replace_with in matches:
        result.extend((text[prev_end:match.start()], replace_with))
        prev_end = match.end()
    result.append(text[prev_end:])
    return "".join(result)


_UWU_MAPPINGS = tuple((m[0], m[1]) for m in uwu_data.mappings)


def owofy(text: str) -> str:
    # con: not that efficient
    # pro: works
    nmsg = []
    if random.randint(0, 10) > 7:
        nmsg.append(random.choice(uwu_data.prefixes) + " ")
    # returns list of words alternating with whitespace (in this order, word may be empty)
    split = re.split(r"(\s+)", text)
    is_seperator = True
    for word in split:
        is_seperator = not is_seperator
        if is_seperator or not word or discord_linkify_likely(word):
            nmsg.append(word)
            continue
        word = replace_non_overlapping(word, _UWU_MAPPINGS)
        if word and random.random() < 0.1 and word[0].isalpha():
            word = f"*{word[0]}-{word[0]}-*{word}"

        nmsg.append(word)
        if word and random.random() < 0.5 and word[-1] in [".", ",", "?"]:
            nmsg.append(" *" + escape_markdown(random.choice(uwu_data.int_emote)) + "*")
    return "".join(nmsg)


def get_random_emote() -> str:
    return random.choice(uwu_data.int_emote)


def get_random_sorry() -> str:
    return random.choice(uwu_data.sowwy)
