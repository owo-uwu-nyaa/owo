import asyncio
import catapi
from discord.ext import commands


class Aww(commands.Cog):

    def __init__(self, bot, bpath):
        self.bot = bot
        catapi_key = open(bpath + "cat_token.owo", "r").read()
        self.catapi = catapi.CatApi(api_key=catapi_key)

    @commands.command(brief="cat")
    async def aww(self, ctx):
        res = await asyncio.get_running_loop().create_task(self.catapi.search_images(limit=1))
        await ctx.send(res[0].url)
