# This is stolen and merged from owoifier https://github.com/FernOfSigma/owoifier/tree/main/owoifier
# and https://github.com/Daniel-Liu-c0deb0t/uwu/blob/uwu/src/lib.rs
# special thanks goes to https://www.reddit.com/r/creepyasterisks/top/?t=year

import re

prefixes = (
    "OwO",
    "OwO what's this?",
    "*nuzzles*",
    "*blushes*",
    "*notices bulge*",
    "K-Konichiwa",
    "*blush*",
    "*heart goes doki-doki*",
    "*boops your nose*",
    "giggles",
    "*gives you headpats*",
    "*wags tail*",
    "*pets you*",
    "*tips fedora*",
)


def rgl(match, group, value) -> str:
    return len(match.group(group)) * value


mappings0 = (
    # ("l", "wl"),
    ("r", "w"),
    ("(?<=[aeiou])l(l+)", r"w\1", "wl+"),
    ("(?<=[aeiou])l", "wl"),
    # ("(?<!w)l", "w"),  # l, not preceded by w
    ("n(a+|e+|i+|o+|u+)", lambda m: "ny" + rgl(m, 1, m.group(1)), "ny(a+|e+|i+|o+|u+)"),
    (r"(?<=\w)ove", "uv"),
    ("small", "smol"),
    ("cute", "kawaii~"),
    ("fluff", "floof"),
    ("love", "luv"),
    ("stupid", "baka"),
    ("what", "nani"),
    ("meow", "nya~"),
    ("(e+)e", lambda m: rgl(m, 1, "e") + "w", "e+w"),
    # ("at", "awt"),
    ("oops", "oopsie woopsie"),
)
mappings = tuple((re.compile(m[0]), m[1], re.compile(m[-1])) for m in mappings0)


int_emote = (
    "rawr x3",
    "OwO",
    "UwU",
    "o.O",
    "-.-",
    ">w<",
    "(⑅˘꒳˘)",
    "(ꈍᴗꈍ)",
    "(˘ω˘)",
    "(U ᵕ U❁)",
    "σωσ",
    "òωó",
    "(///ˬ///✿)",
    "(U ﹏ U)",
    "( ͡o ω ͡o )",
    "ʘwʘ",
    ":3",
    "XD",
    "nyaa~~",
    "mya",
    ">_<",
    "😳",
    "🥺",
    "😳😳😳",
    "rawr",
    "^^",
    "^^;;",
    " (ˆ ﻌ ˆ)♡",
    " ^•ﻌ•^",
    " /(^•ω•^)",
    " (✿oωo)",
    "^w^",
    "(◕ᴥ◕)",
    "ʕ•ᴥ•ʔ",
    "ʕ￫ᴥ￩ʔ",
    # "(*^ω^)",
    "(◕‿◕✿)",
    # "(*^.^*)",
    # "(*￣з￣)",
    "(つ✧ω✧)つ",
    "(/ =ω=)/",
    ">///<",
    "-w-",
    "QwQ",
)

sowwy = (
    "sowwy",
    "owo nowww",
    "nowo",
    "owupsie",
    "I'm sowwwyy ~~",
    "nani?",
    "s-s-sadwy you cwannot dow that",
    "i w-want to compwy, mwaster, but i cwannot",
    "Baka!",
)

good_owo_spirit = (
    "umu",
    "owo",
    "uwu",
    "~~~",
    "senpai",
    "oni",
    "chan",
    "nicole",
    "desu",
    "nowu",
    "desu",
    "haj",
    "wolf",
    "neko",
    "kon",
)
