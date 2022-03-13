from datetime import datetime

from discord.ext import commands


class MsgWriter(commands.Cog):

    def __init__(self, bot, config):
        self.bot = bot
        self.datalake = config.datalake

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        self.datalake.put_row("msgs", {'snowflake': message.id, "author_id": message.author.id,
                                               "channel_id": message.channel.id, "guild_id": message.guild.id,
                                               "time": datetime.now(), "msg": message.content})