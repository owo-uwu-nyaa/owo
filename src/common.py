import re
import discord


def get_nick_or_name(user: object) -> str:
    gnick = user.nick if isinstance(user, discord.Member) and not user.nick is None else user.name
    return re.sub(r'[@!$`]', "", gnick)
