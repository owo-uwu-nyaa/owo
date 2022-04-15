import logging
from os import path
import subprocess
import sys
import discord
from discord.ext import commands
from owobot.misc import common
from owobot.misc.database import Owner, MusicChan
import yt_dlp

log = logging.getLogger(__name__)


class Restricted(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await common.is_owner(ctx)

    @commands.command(aliases=["cwash"])
    async def crash(self):
        sys.exit(0)

    @commands.command()
    async def parrot(self, ctx, *, msg: str):
        await ctx.send(msg)

    @commands.command(aliases=["redwepoy"])
    async def redeploy(self, ctx):
        (src_path, _) = path.split(path.realpath(__file__))
        uwu = subprocess.run(["git", "pull"], capture_output=True, cwd=src_path, check=False)
        await ctx.send(f"```\n{uwu}\n```")
        sys.exit(0)

    @commands.Cog.listener()
    async def on_ready(self):
        log.info(f"Hewoo, my name is {self.bot.user}")

    @commands.group()
    async def owner(self, ctx):
        pass

    @owner.command(name="add", brief="add an owner")
    async def owner_add(self, ctx, member: discord.Member):
        query = Owner.insert(snowflake=member.id)
        await common.try_exe_cute_query(ctx, query)

    @owner.command(name="rm", brief="remove an owner")
    async def owner_rm(self, ctx, member: discord.Member):
        query = Owner.delete().where(Owner.snowflake == member.id)
        await common.try_exe_cute_query(ctx, query)

    @commands.group()
    async def music_chan(self, ctx):
        pass

    @music_chan.command(name="add", brief="add a music_chan")
    async def music_chan_add(self, ctx):
        query = MusicChan.insert(channel=ctx.channel.id)
        await common.try_exe_cute_query(ctx, query)

    @music_chan.command(name="rm", brief="remove a music_chan")
    async def music_chan_rm(self, ctx):
        query = MusicChan.delete().where(MusicChan.channel == ctx.channel.id)
        await common.try_exe_cute_query(ctx, query)


def setup(bot):
    bot.add_cog(Restricted(bot))
