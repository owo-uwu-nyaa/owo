import os

os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.kudu:kudu-spark3_2.12:1.15.0 pyspark-shell'
import discord
from discord.ext.commands import Bot as BotBase
from owobot.misc.config import Config


class OwOBot(BotBase):
    def __init__(self, config_path):
        config = Config(config_path)

        intents = discord.Intents().all()
        allowed_mentions = discord.AllowedMentions(
            users=True, everyone=False, roles=False, replied_user=False)
        super().__init__(command_prefix=config.command_prefix, description=config.desc, intents=intents,
                         allowed_mentions=allowed_mentions)
        self.config = config

        src_dir, _ = os.path.split(os.path.realpath(__file__))
        cog_path = os.path.join(src_dir, "cogs")
        cogs = [os.path.splitext(f)[0] for f in os.listdir(cog_path)
                if f.endswith(".py")]
        cogs = list(filter(lambda x: x not in config.blocked_cogs, cogs))
        for cog in cogs:
            self.load_extension(f"owobot.cogs.{cog}")

    def run(self):
        print("running bot..")
        super().run(self.config.discord_token, reconnect=True)
