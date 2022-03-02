import os
import os.path as path
import subprocess
import sys

from discord.ext import commands


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["cwash"])
    async def crash(self, ctx):
        sys.exit(0)

    @commands.command(aliases=["redwepoy"])
    async def redeploy(self, ctx):
        #get path of src dir, no need for passing it as a variable
        (src_path,_)=path.split(path.realpath(__file__))
        uwu = subprocess.run(["git", "pull"], capture_output=True,cwd=src_path)
        await ctx.send(f"```\n{uwu}\n```")
        sys.exit(0)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Hewoo, my name is", self.bot.user)
