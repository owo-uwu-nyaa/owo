from discord.ext import commands
import bottom


class Bottom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(aliases=["bowottom"])
    async def bottom(self, ctx, *, msg: str):
        await ctx.send(bottom.encode(msg))

    @commands.hybrid_command(aliases=["unbowottom"])
    async def unbottom(self, ctx, *, msg: str):
        await ctx.send(bottom.decode(msg))


def setup(bot):
    return bot.add_cog(Bottom(bot))
