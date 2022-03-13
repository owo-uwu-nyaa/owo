import re
import discord


def get_nick_or_name(user: object) -> str:
    gnick = user.nick if isinstance(user, discord.Member) and not user.nick is None else user.name
    return re.sub(r'[@!$`]', "", gnick)


async def author_id_to_obj(bot, author_id, ctx):
    author = ctx.guild.get_member(author_id)
    if author is None:
        author = await bot.fetch_user(author_id)
    return author


markdown_chars = ["~", "_", "*", "`"]

def sanitize(str: str) -> str:
    # prepend each markdown interpretable char with a zero width space
    # italics with a single * seems to not break codeblocks
    for c in markdown_chars:
        if c in str:
            str = str.replace(c, f"​{c}")
    return str
