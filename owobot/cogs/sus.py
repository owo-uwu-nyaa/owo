import logging
import re
import functools
import time
from datetime import timedelta
import itertools as it
import more_itertools as mit

import discord
from discord.ext import commands

from owobot.owobot import OwOBot
from owobot.misc import common, suslib, owolib, discord_emoji


from typing import Optional


log = logging.getLogger(__name__)


class Sus(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot

    _EMOJI_RE = re.compile(":?(?P<name>[^:]+):?")

    @classmethod
    @functools.lru_cache(maxsize=None)  # equivalent to functools.cache in python >= 3.10
    def _emoji_names_dictionary(cls):
        log.info("start building emoji name dictionary")
        start = time.process_time_ns()

        result = suslib.build_dictionary(
            name.lower()
            for name, emoji in discord_emoji.EMOJIS_BY_NAME.items()
            if not isinstance(emoji, discord_emoji.DiversityChild)
        )

        end = time.process_time_ns()
        log.info("finished building emoji dictionary in %s", timedelta(microseconds=(end - start) // 1000))

        return result

    @classmethod
    def build_emoji_name_dictionary(cls):
        cls._emoji_names_dictionary()

    @commands.hybrid_command(
        brief="find the shortest way to describe an emoji when inputting it on this server :postbox:"
    )
    @common.long_running_command
    async def sus(
            self,
            ctx: commands.Context,
            emoji: str,
            nitro: Optional[bool] = None,
            include_builtin=True
    ):
        if emoji in discord_emoji.EMOJIS_BY_SURROGATES:
            emoji_str = builtin_emoji = discord_emoji.EMOJIS_BY_SURROGATES[emoji]
            candidates = builtin_emoji.names
            nitro = False if nitro is None else nitro
        else:
            emoji_str = server_emoji = discord.PartialEmoji.from_str(emoji)
            candidates = (server_emoji.name, )
            nitro = server_emoji.animated if nitro is None else nitro

        server_dictionary = suslib.build_dictionary(
            emoji.name.lower() for emoji in ctx.guild.emojis if nitro or not emoji.animated
        )

        suss_per_candidate = (
            suslib.shortest_unique_substring(
                candidate.lower(),
                *(Sus._emoji_names_dictionary(),) if include_builtin else (),
                server_dictionary)
            for candidate in candidates
        )

        suss = tuple(map(lambda sus: f"`{sus}`", mit.unique_everseen(it.chain.from_iterable(common.minima(
            suss_per_candidate,
            # put non-empty result tuples first, then sort by the length of the shortest unique substring(s)
            key=lambda suss0: (0, suss0[0]) if suss0 else (1, None)
        )))))

        await ctx.send(
            f"shortest way to describe {emoji_str} is "
            + ", ".join(suss[:-1]) + (" or " if len(suss) > 1 else "") + suss[-1]
            if suss
            else f"{owolib.get_random_sorry()}: {owolib.owofy('no unique way to describe')} {emoji_str}"
        )


async def setup(bot):
    Sus.build_emoji_name_dictionary()
    await bot.add_cog(Sus(bot))
