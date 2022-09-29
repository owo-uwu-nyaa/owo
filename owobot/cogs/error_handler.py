from __future__ import annotations

import asyncio
import sys
import logging
import traceback
import random

import discord
from discord.ext import commands
from discord.ext.commands import Context

from owobot.misc import owolib
from owobot.misc.common import nullable_dict
from owobot.owobot import OwOBot

from typing import Optional, List

log = logging.getLogger(__name__)


def _format_unhandled_exception(error):
    err_str = traceback.format_exception_only(type(error), error)[-1].strip()
    return f"An unhandled exception occurred. Check the logs for details.\n```\n{err_str}\n```"


async def _reply_on_error(reply_to, message: str):
    print(reply_to.channel.id)
    if reply_to.channel.id in [1007320173625221291, 1007320293079011528, 1007320154734080000, 1008432834983235754]:
        return
    await reply_to.reply(
        message,

        **nullable_dict(

            # for text-based commands: delete after one minute
            mention_author=False,
            delete_after=60,

            # for interaction (slash) commands: "ephemeral" message which can be clicked away
            ephemeral=True if isinstance(reply_to, commands.Context) else None
        )
    )


def _format_suggested_commands(text, suggestions: List[OwOBot.command_suggestion]):
    esc = discord.utils.escape_markdown
    return (
        f"Command `{esc(text)}` not found"
        + (
            ", did you mean:\n"
            + "\n".join(
                "‣ "
                + (
                    f"command `{esc(suggestion.name)}`"
                    if suggestion.name == suggestion.command.name
                    else f"`{esc(suggestion.name)}` (alias for command `{esc(suggestion.command.name)}`)"
                )
                + (f"{' ' * 8}*{esc(suggestion.command.brief)}*" if suggestion.command.brief else "")
                for suggestion in suggestions
            )
            if suggestions
            else "."
        )
    )


# handles event errors
def _mk_on_error(error_handler: ErrorHandler):
    async def handler(event, *args, **kwargs):
        # in on_error, sys.exc_info() works
        log.exception(f"unhandled exception in event handler '{event}'")

        reply_to: Optional[discord.Message | Context | discord.PartialMessage] = None
        if event == "on_message":
            reply_to = args[0]
        elif event == "on_command_error":
            ctx: Context = args[0]
            reply_to = ctx
        elif event in ("on_raw_reaction_add", "on_raw_reaction_remove"):
            rct: discord.RawReactionActionEvent = args[0]
            reply_to = error_handler.bot.get_partial_messageable(rct.channel_id).get_partial_message(rct.message_id)

        if reply_to is not None:
            _, value, _ = sys.exc_info()
            await _reply_on_error(reply_to, _format_unhandled_exception(value))

    return handler


class ErrorHandler(commands.Cog):
    def __init__(self, bot: OwOBot):
        super().__init__()
        self.bot = bot
        bot.on_error = _mk_on_error(self)

    @classmethod
    def _tantrum(cls):
        raise random.choice(
            [ValueError, TypeError, ArithmeticError, AttributeError, KeyError, NameError]
        )(owolib.owofy("screaming and crying rn"))

    @commands.hybrid_command(brief="screaming and crying rn")
    async def tantrum(self, ctx: Context):
        ErrorHandler._tantrum()

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            await asyncio.sleep(1)
            dynamic_command = self.bot.check_dynamic(ctx.message)
            if not dynamic_command:
                suggestions = self.bot.suggest_commands(ctx.invoked_with)
                await _reply_on_error(ctx, _format_suggested_commands(ctx.invoked_with, suggestions))
            return
        if isinstance(error, commands.CommandOnCooldown):
            await _reply_on_error(ctx, f"{owolib.get_random_sorry()}: {owolib.owofy(str(error))}")
            return
        log.error("unhandled exception in command", exc_info=error)
        await _reply_on_error(ctx, _format_unhandled_exception(error))


def setup(bot):
    return bot.add_cog(ErrorHandler(bot))
