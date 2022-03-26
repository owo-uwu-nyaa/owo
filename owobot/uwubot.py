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
        allowed_mentions = discord.AllowedMentions(users=True, everyone=False, roles=False, replied_user=False)
        super().__init__(command_prefix=config.command_prefix, description=config.desc, intents=intents,
                         allowed_mentions=allowed_mentions)
        self.config = config

        # Load cogs
        src_dir, _ = path.split(path.realpath(__file__))
        cogs_path = path.join(src_dir, "../cogs")
        cogs = os.listdir(cogs_path)

        # TODO: temporary fix as cogs not working
        blocked_cogs = ["gallery.py", "msg_writer.py", "stats.py"]
        cogs = list(filter(lambda x: x not in blocked_cogs, cogs))

        for cog in cogs:
            importlib.import_module(cog)
        
        # TODO: dynamically add cogs to bot
