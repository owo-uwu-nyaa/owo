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
from config import Config


def main():
    config_file="owo.toml"
    if len(sys.argv)>1:
        config_file=sys.argv[1]
    config=Config(config_file)
    intents = discord.Intents().all()
    allowed_mentions = discord.AllowedMentions(users=True, everyone=False, roles=False, replied_user=False)
    bot = commands.Bot(command_prefix=config.command_prefix, description=config.desc, intents=intents, allowed_mentions=allowed_mentions)

    bot.add_cog(Hugs(bot))
    bot.add_cog(MsgWriter(bot, config.message_file))
    bot.add_cog(Aww(bot, config.catapi_token))
    bot.add_cog(Misc(bot))
    bot.add_cog(Owo(bot))
    bot.add_cog(Admin(bot))
    bot.add_cog(Stats(bot, config.message_file))
    bot.add_cog(Bottom(bot, config.bottom_cmd))
    # bot.add_cog(Quotes(bot))
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start(config.discord_token))
    loop.run_forever()


if __name__ == '__main__':
    main()
