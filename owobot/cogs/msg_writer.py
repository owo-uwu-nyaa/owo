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
        self.datalake.put_row("msgs", {"msg_id": message.id, "author_id": message.author.id,
                                       "channel_id": message.channel.id, "guild_id": message.guild.id,
                                       "time": datetime.now(), "msg": message.content})

    @commands.Cog.listener()
    async def on_raw_typing(self, payload):
        self.datalake.put_row("typing", {"author_id": payload.user_id,
                                         "channel_id": payload.channel_id, "guild_id": payload.guild_id,
                                         "time": payload.when})

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        self.datalake.put_row("delete", {"msg_id": payload.message_id,
                                         "channel_id": payload.channel_id, "guild_id": payload.guild_id,
                                         "time": datetime.now()})

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        for msg_id in payload.message_ids:
            self.datalake.put_row("delete", {"msg_id": msg_id,
                                             "channel_id": payload.channel_id, "guild_id": payload.guild_id,
                                             "time": datetime.now()})

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        nmsg = ""
        if payload.data["content"] != None:
            nmsg = payload.data["content"]
        self.datalake.put_row("edit",
                              {"msg_id": payload.message_id, "channel_id": payload.channel_id,
                               "guild_id": payload.guild_id,
                               "time": datetime.now(), "nmsg": nmsg})

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        self.datalake.put_row("react",
                              {"msg_id": payload.message_id, "channel_id": payload.channel_id,
                               "guild_id": payload.guild_id,
                               "author_id": payload.user_id, "added": True,
                               "time": datetime.now(), "emoji": str(payload.emoji)})

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        self.datalake.put_row("react",
                              {"msg_id": payload.message_id, "channel_id": payload.channel_id,
                               "guild_id": payload.guild_id,
                               "author_id": payload.user_id, "added": False,
                               "time": datetime.now(), "emoji": str(payload.emoji)})

    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload):
        self.datalake.put_row("clear",
                              {"msg_id": payload.message_id, "channel_id": payload.channel_id,
                               "guild_id": payload.guild_id,
                               "time": datetime.now(), "emoji": str(payload.emoji)})

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if (before.status != after.status):
            self.datalake.put_row("presence", {"author_id": before.id, "time": datetime.now(), "before": str(before.status),
                                           "after": str(after.status)})
