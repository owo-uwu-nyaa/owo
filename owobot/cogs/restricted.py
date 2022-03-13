import os.path as path
import subprocess
import sys

import discord
from discord.ext import commands

from misc.db import Admin


class Restricted(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot

    async def cog_check(self, ctx):
        return Admin.select().where(Admin.snowflake == ctx.author.id).exists()

    @commands.command(aliases=["cwash"])
    async def crash(self):
        sys.exit(0)

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
        Admin.create(snowflake=member.id)

    @owner.command(brief="remove an owner")
    async def remove(self, ctx, member: discord.Member):
        Admin.delete().where(Admin.snowflake == member.id).execute()