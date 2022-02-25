import subprocess
from discord.ext import commands


class Bottom(commands.Cog):

    def __init__(self, bot, bpath):
        self.bpath = bpath
        self.bot = bot

    @commands.command()
    async def bottom(self, ctx, *, msg: str):
        bottom = subprocess.run([self.bpath + "bottomify", "-b", msg], capture_output=True)
        await ctx.send(bottom.stdout.decode("utf8"))

    @commands.command()
    async def unbottom(self, ctx, *, msg: str):
        uwu = subprocess.run([self.bpath + "bottomify", "-r", msg], capture_output=True)
        await ctx.send(uwu.stdout.decode("utf8"))
