import discord
from owobot.cogs.e621 import E621
from discord.ext import commands
from owobot.misc import common
from owobot.misc.database import KirbySpam


class Kirby(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def kirby(self, ctx):
        pass

    @kirby.command(name="add", brief="add user to getting spammed")
    async def kirby_add(self, ctx, member: discord.Member):
        query = KirbySpam.insert(user_id=member.id)
        await common.try_exe_cute_query(ctx, query)

    @kirby.command(name="remove", alias=["rm"], brief="remove user from spam list")
    async def kirby_remove(self, ctx, member: discord.Member):
        query = KirbySpam.delete().where(KirbySpam.user_id == member.id)
        await common.try_exe_cute_query(ctx, query)

    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.author == self.bot.user
                or not KirbySpam.select().where(KirbySpam.user_id == message.author.id).exists()):
            return

        f = E621._create_basefurl().add({"tags": "kirby order:random", "limit": "1"})
        posts = await E621._get_posts(f.url)
        await message.channel.send(posts[0]["file"]["url"])


def setup(bot):
    bot.add_cog(Kirby(bot))
