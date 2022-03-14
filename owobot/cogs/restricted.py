import os.path as path
import subprocess
import sys

import discord
from discord.ext import commands

import misc.common
from misc import common
from misc.db import Owner, HugShort


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
        uwu = subprocess.run(["git", "pull"], capture_output=True, cwd=src_path)
        await ctx.send(f"```\n{uwu}\n```")
        sys.exit(0)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Hewoo, my name is", self.bot.user)

    @commands.group()
    async def owner(self, ctx):
        pass

    @owner.command(brief="add an owner")
    async def add(self, ctx, member: discord.Member):
        try:
            Owner.create(snowflake=member.id)
            await common.react_success(ctx)
        except:
            await common.react_failure(ctx)

    @owner.command(brief="remove an owner")
    async def rm(self, ctx, member: discord.Member):
        try:
            Owner.delete().where(Owner.snowflake == member.id).execute()
            await common.react_success(ctx)
        except:
            await common.react_failure(ctx)