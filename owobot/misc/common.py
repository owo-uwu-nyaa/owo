import datetime
import re
import discord
import emoji
from peewee import PeeweeException
from owobot.misc.database import Owner


def get_nick_or_name(user: object) -> str:
    gnick = (
        user.nick
        if isinstance(user, discord.Member) and not user.nick is None
        else user.name
    )
    return re.sub(r"[@!$`]", "", gnick)


async def author_id_to_obj(bot, author_id, ctx):
    author = ctx.guild.get_member(author_id)
    if author is None:
        author = await bot.fetch_user(author_id)
    return author


markdown_chars = ["~", "_", "*", "`"]


def sanitize_markdown(text: str) -> str:
    # prepend each markdown interpretable char with a zero width space
    # italics with a single * seems to not break codeblocks
    for char in markdown_chars:
        if char in text:
            text = text.replace(char, f"​{char}")
    return text


def sanitize_send(text: str) -> str:
    if text[0] in emoji.EMOJI_UNICODE_ENGLISH:
        return text
    return re.sub(r"^[^\w<>()@*_~`]+", "", text)


async def is_owner(ctx):
    if Owner.select().where(Owner.snowflake == ctx.author.id).exists():
        return True
    await react_failure(ctx)
    return False


async def react_success(ctx):
    await ctx.message.add_reaction("✅")


async def react_failure(ctx):
    await ctx.message.add_reaction("❌")


async def react_empty(ctx):
    await ctx.message.add_reaction("🧺")


async def try_exe_cute_query(ctx, query):
    try:
        res = query.execute()
        await react_success(ctx)
        return res
    except PeeweeException:
        await react_failure(ctx)

#from https://github.com/janin-s/ki_pybot/blob/8d1cf55aaafe991bd8e021c8d72e5df5e0ee42de/lib/utils/trading_utils.py#L247
def seconds_until(hours: int, minutes: int) -> float:
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time)  # days always >= 0

    return (future_exec - now).total_seconds()
