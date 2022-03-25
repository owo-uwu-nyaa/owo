#! /bin/python3
import asyncio
import sys
import discord
from discord.ext import commands
from cogs.admin import Admin
from cogs.e621 import E621
from cogs.restricted import Restricted
from cogs.aww import Aww
from cogs.bottom import Bottom
from cogs.hugs import Hugs
from cogs.msg_writer import MsgWriter
from cogs.simple_commands import Misc
from cogs.owo import Owo
from cogs.kirby import Kirby
from cogs.stats import Stats
from cogs.t_game import T_game
from misc.config import Config
from cogs.gallery import Gallery


def main():
    # TODO: refactor to use uwubot.py class
    config_file = "owo.toml"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    config = Config(config_file)

    intents = discord.Intents().all()
    allowed_mentions = discord.AllowedMentions(users=True, everyone=False, roles=False, replied_user=False)
    bot = commands.Bot(command_prefix=config.command_prefix, description=config.desc, intents=intents,
                       allowed_mentions=allowed_mentions)

    bot.add_cog(Hugs(bot))
    bot.add_cog(MsgWriter(bot))
    bot.add_cog(Aww(bot))
    bot.add_cog(Misc(bot))
    bot.add_cog(Owo(bot))
    bot.add_cog(Kirby(bot))
    bot.add_cog(Restricted(bot))
    bot.add_cog(Admin(bot))
    bot.add_cog(Gallery(bot))
    bot.add_cog(Stats(bot))
    bot.add_cog(Bottom(bot))
    bot.add_cog(E621(bot))
    bot.add_cog(T_game(bot))
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start(config.discord_token))

    loop.run_forever()


if __name__ == '__main__':
    main()
