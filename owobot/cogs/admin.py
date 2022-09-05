from discord.ext import commands
from discord.ext.commands import Bot
from owobot.misc import common
from owobot.misc.database import NsflChan, OwoChan, RainbowGuild


class Admin(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.hybrid_group()
    async def mark(self, ctx: commands.Context):
        pass

    @mark.command(name="nsfl", brief="mark this as nsfl channel")
    async def mark_nsfl(self, ctx):
        query = NsflChan.insert(channel=ctx.channel.id)
        await common.try_exe_cute_query(ctx, query)

    @mark.command(name="owo", brief="mark this as a channel that should be owofied")
    async def mark_owo(self, ctx):
        query = OwoChan.insert(channel=ctx.channel.id)
        await common.try_exe_cute_query(ctx, query)

    @mark.command(name="rainbow", brief="mark this guild as a rainbow guild")
    async def mark_rainbow(self, ctx):
        query = RainbowGuild.insert(snowflake=ctx.guild.id)
        await common.try_exe_cute_query(ctx, query)

    @commands.hybrid_group()
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

    @unmark.command(name="rainbow", brief="unmark this guild as a rainbow guild")
    async def unmark_rainbow(self, ctx):
        query = OwoChan.delete().where(RainbowGuild.snowflake == ctx.guild.id)
        await common.try_exe_cute_query(ctx, query)

    @commands.hybrid_command(brief="sync slash commands to the current guild")
    async def sync(self, ctx: commands.Context):
        self.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await self.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(synced)} slash command(s) to **{ctx.guild.name}**.")


def setup(bot):
    return bot.add_cog(Admin(bot))
