import asyncio
import catapi
from discord.ext import commands


class Aww(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.catapi = catapi.CatApi(api_key=bot.config.catapi_token)

    @commands.command(brief="cat")
    async def aww(self, ctx):
        res = await asyncio.get_running_loop().create_task(self.catapi.search_images(limit=1))
        await ctx.send(res[0].url)


def setup(bot):
    bot.add_cog(Aww(bot))
