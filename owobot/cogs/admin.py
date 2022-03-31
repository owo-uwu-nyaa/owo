from discord.ext import commands
from owobot.misc import common
from owobot.misc.database import NsflChan, OwoChan


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.group()
    async def mark(self, ctx):
        pass

    @mark.command(name="nsfl", brief="mark this as nsfl channel")
    async def mark_nsfl(self, ctx):
        query = NsflChan.insert(channel=ctx.channel.id)
        await common.try_exe_cute_query(ctx, query)

    @mark.command(name="owo", brief="mark this as a channel that should be owofied")
    async def mark_owo(self, ctx):
        query = OwoChan.insert(channel=ctx.channel.id)
        await common.try_exe_cute_query(ctx, query)

    @commands.group()
    async def unmark(self, ctx):
        pass

    @unmark.command(name="nsfl", brief="unmark this as nsfl channel")
    async def unmark_nsfl(self, ctx):
        query = NsflChan.delete().where(NsflChan.channel == ctx.channel.id)
        await common.try_exe_cute_query(ctx, query)

    @unmark.command(name="owo", brief="unmark this as an owo channel")
    async def unmark_owo(self, ctx):
        query = OwoChan.delete().where(OwoChan.channel == ctx.channel.id)
        await common.try_exe_cute_query(ctx, query)


def setup(bot):
    bot.add_cog(Admin(bot))
