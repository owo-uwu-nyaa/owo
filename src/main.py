#! /bin/python3
import asyncio
import sys
import discord
from discord.ext import commands
from admin import Admin
from aww import Aww
from bottom import Bottom
from hugs import Hugs
from msg_writer import MsgWriter
from simple_commands import Misc
from owo import Owo
from stats import Stats


def main():
    react_on = "$"
    bpath = f"{sys.argv[1]}/"
    token = open(bpath + "token.owo", "r").read()
    desc = "Pwease end my misewy, nyaaa~"
    intents = discord.Intents().all()
    allowed_mentions = discord.AllowedMentions(users=True, everyone=False, roles=False, replied_user=False)
    bot = commands.Bot(command_prefix=react_on, description=desc, intents=intents, allowed_mentions=allowed_mentions)

    bot.add_cog(Hugs(bot))
    bot.add_cog(MsgWriter(bot, bpath))
    bot.add_cog(Aww(bot, bpath))
    bot.add_cog(Misc(bot))
    bot.add_cog(Owo(bot))
    bot.add_cog(Admin(bot, bpath))
    bot.add_cog(Stats(bot, bpath))
    bot.add_cog(Bottom(bot, bpath))
    # bot.add_cog(Quotes(bot))
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start(token))
    loop.run_forever()


if __name__ == '__main__':
    main()
