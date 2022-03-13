from discord.ext import commands

from misc.db import NsflChan


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.group()
    async def nsfl(self, ctx):
        pass

    @nsfl.command(brief="mark this as nsfl channel")
    async def mark(self, ctx):
        NsflChan.create(channel=ctx.channel.id)

    @nsfl.command(brief="unmark this as nsfl channel")
    async def unmark(self, ctx):
        NsflChan.delete().where(NsflChan.channel == ctx.channel.id).execute()