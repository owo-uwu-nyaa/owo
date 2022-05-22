import asyncio.subprocess as sub
from discord.ext import commands


class Bottom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bottom_cmd = bot.config.bottom_cmd

    async def call_bottom(self, arg: str, msg: str):
        if msg.startswith("-"):
            # prepend zero width space to prevent interpretation as command line argument
            msg = "\ue2808b" + msg
        process = await sub.create_subprocess_exec(
            self.bottom_cmd,
            arg,
            msg,
            stdin=sub.PIPE,
            stdout=sub.PIPE,
            stderr=sub.DEVNULL,
        )
        (uwu, _) = await process.communicate()
        return uwu.decode("utf-8")

    @commands.command(aliases=["bowottom"])
    async def bottom(self, ctx, *, msg: str):
        bottom = await self.call_bottom("-b", msg)
        await ctx.send(bottom)

    @commands.command(aliases=["unbowottom"])
    async def unbottom(self, ctx, *, msg: str):
        uwu = await self.call_bottom("-r", msg)
        await ctx.send(uwu)


def setup(bot):
    bot.add_cog(Bottom(bot))
