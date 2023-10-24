from discord.ext import commands
from discord.ext.commands import Bot
from owobot.misc import common
from owobot.misc.database import NsflChan, OwoChan, RainbowGuild, ForceEmbed, EvilTrackingParameter


class Admin(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator
    
    @commands.hybrid_command()
    async def purge(self, ctx, n):
        n = int(n)
        if n < 1 or n >= 50:
            return

        msg = await ctx.send(f"Deleting {n} message(s)...")
        deleted = await ctx.channel.purge(limit=int(n), bulk=True, check=lambda m: m != msg and m != ctx.message)
        await msg.edit(content=f'Sucessfully deleted {len(deleted)} message(s)')

    @commands.hybrid_command()
    async def add_embed_url(self, ctx, domain, new_domain):
        query = ForceEmbed.insert(url=domain, new_url=new_domain).on_conflict("replace")
        await common.try_exe_cute_query(ctx, query)

    @commands.hybrid_command()
    async def add_evil_parameter(self, ctx, domain, parameter_name):
        query = EvilTrackingParameter.insert(url=domain, tracking_parameter=parameter_name).on_conflict("replace")
        await common.try_exe_cute_query(ctx, query)

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
        await ctx.send(f":3 Syncing {len(self.bot.cogs)} from a total of {self.bot.total_cog_count} cogs...")

        self.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await self.bot.tree.sync(guild=ctx.guild)
        await ctx.send(
            f"Synced {len(synced)} slash command(s) to **{ctx.guild.name}**."
        )

        if self.bot.error_cog_count > 0:
            await ctx.send(f"⚠ Due to errors when loading the cogs, {self.bot.error_cog_count} cog(s) have been skipped. Some commands may not have been synced properly.")


def setup(bot):
    return bot.add_cog(Admin(bot))
