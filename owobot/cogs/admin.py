import os.path as path
import subprocess
import sys

from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.bot_owner = config.bot_owner

    async def cog_check(self, ctx):
        return ctx.author.id in self.bot_owner

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