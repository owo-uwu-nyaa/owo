import os
from os import path
import discord
import importlib
from misc.config import Config
from discord.ext.commands import Bot as BotBase


class UwuBot(BotBase):
    def __init__(self, config_path):
        config = Config(config_path)

        intents = discord.Intents().all()
        allowed_mentions = discord.AllowedMentions(
            users=True, everyone=False, roles=False, replied_user=False)
        super().__init__(command_prefix=config.command_prefix, description=config.desc, intents=intents,
                         allowed_mentions=allowed_mentions)
        self.config = config

        # Load cogs
        cogs = [os.path.splitext(f)[0] for f in os.listdir("cogs")
                if f.endswith(".py")]

        # TODO: temporary fix as cogs not working
        blocked_cogs = ["gallery", "msg_writer", "stats", "quotes"]
        cogs = list(filter(lambda x: x not in blocked_cogs, cogs))

        for cog in cogs:
            module = __import__("cogs.%s" % cog, globals(),
                                locals(), fromlist=["*"])

            for item_name in dir(module):
                try:
                    new_cog = getattr(module, item_name)()
                    self.add(new_cog)
                except:
                    pass
