import logging
from os import path
import subprocess
import sys
import discord
from discord.ext import commands
from owobot.misc import common
from owobot.misc.database import Owner
import asyncio.subprocess as sub

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

    @commands.command()
    async def dl(self, ctx, arg: str):
        if arg.startswith("-"):
            # prepend zero width space to prevent interpretation as command line argument
            arg = "\ue2808b" + arg
        process = await sub.create_subprocess_exec(
            "yt-dlp",
            f'-x -o "/srv/navidrome/Youtube/%(title)s.%(ext)s" {arg}',
            stdin=sub.PIPE,
            stdout=sub.PIPE,
            stderr=sub.DEVNULL
        )
        (uwu, _) = await process.communicate()
        return uwu.decode("utf-8")

def setup(bot):
    bot.add_cog(Restricted(bot))
