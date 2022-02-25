import os
import subprocess
import sys

from discord.ext import commands


class Admin(commands.Cog):

    def __init__(self, bot, bpath):
        self.bot = bot
        self.bpath = bpath

    @commands.command()
    async def crash(self, ctx):
        sys.exit(0)

    @commands.command()
    async def redeploy(self, ctx):
        os.chdir(self.bpath)
        uwu = subprocess.run(["git", "pull"], capture_output=True)
        await ctx.send(f"```\n{uwu}\n```")
        sys.exit(0)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Hewoo, my name is", self.bot.user)
