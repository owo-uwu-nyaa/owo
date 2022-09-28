import logging
import re
import functools
import time
from datetime import timedelta
from pathlib import Path

import discord
from discord.ext import commands
import emoji as emojilib

from owobot import misc
from owobot.owobot import OwOBot
from owobot.misc import common, suslib, owolib

from typing import Optional


log = logging.getLogger(__name__)


class Sus(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot

    _EMOJI_RE = re.compile(":?(?P<name>[^:]+):?")

    @classmethod
    @functools.lru_cache(maxsize=None)  # equivalent to functools.cache in python >= 3.10
    def _emoji_names_dictionary(cls):
        data_file = Path(misc.__file__).parent / "emoji_list"
        emoji_names = []
        with data_file.open("r") as df:
            for line in filter(lambda sl: sl, (l.strip() for l in df)):
                emoji_names.append(line.split(" ")[0].lower())

        log.info(f"loaded {len(emoji_names)} emoji names from disk")

        return suslib.build_dictionary(emoji_names)

    @classmethod
    def build_emoji_name_dictionary(cls):
        log.info("start building emoji name dictionary")
        start = time.process_time_ns()
        cls._emoji_names_dictionary()
        end = time.process_time_ns()
        log.info("finished building emoji dictionary in %s", timedelta(microseconds=(end - start) // 1000))

    @commands.hybrid_command(
        brief="find the shortest way to describe an emoji when inputting it on this server :postbox:"
    )
    @common.long_running_command
    async def sus(self, ctx: commands.Context, emoji: str, nitro: Optional[bool] = None, include_builtin=True):
        if emoji in emojilib.EMOJI_DATA:
            emoji_repr = emoji
            # TODO?: check all aliases, also not fully correct
            emoji_name = Sus._EMOJI_RE.fullmatch(emojilib.EMOJI_DATA[emoji]["en"])["name"]
            nitro = False if nitro is None else nitro
        else:
            emoji_repr = d_emoji = discord.PartialEmoji.from_str(emoji)
            emoji_name = d_emoji.name
            nitro = d_emoji.animated if nitro is None else nitro
        suss = tuple(map(
            lambda su: f"`{su}`",
            suslib.shortest_unique_substring(
                emoji_name.lower(),
                *(Sus._emoji_names_dictionary(),) if include_builtin else (),
                suslib.build_dictionary(
                    emoji.name.lower()
                    for emoji in ctx.guild.emojis
                    if nitro or not emoji.animated)
            )
        ))

        await ctx.send(
            f"shortest way to describe {emoji_repr} is "
            + ", ".join(suss[:-1]) + (" or " if len(suss) > 1 else "") + suss[-1]
            if suss
            else f"{owolib.get_random_sorry()}: {owolib.owofy('no unique way to describe')} {emoji_repr}"
        )


def setup(bot):
    Sus.build_emoji_name_dictionary()
    return bot.add_cog(Sus(bot))
