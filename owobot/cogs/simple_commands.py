import datetime
import io
import random

import discord
import pandas as pd
import plotly.express as px
import requests
from discord.ext import commands

from owobot.misc import common, owolib
from owobot.owobot import OwOBot


class SimpleCommands(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot

    @commands.hybrid_command(name="obamamedal")
    async def obamamedal(self, ctx):
        await ctx.send(
            "https://media.discordapp.net/attachments/798609300955594782/816701722818117692/obama.jpg"
        )

    @commands.hybrid_command()
    async def owobamamedal(self, ctx):
        await ctx.send(
            "https://cdn.discordapp.com/attachments/938102328282722345/939605208999264367/Unbenannt.png"
        )

    @commands.hybrid_command(aliases=["hewwo"])
    async def hello(self, ctx):
        await ctx.send(random.choice(["Hello", "Hello handsome :)"]))

    @commands.hybrid_command(aliases=["evewyone"])
    async def everyone(self, ctx):
        await ctx.send("@everyone")

    @commands.hybrid_command(brief="OwO")
    async def owo(self, ctx):
        await ctx.send(owolib.get_random_emote())

    @commands.hybrid_command(brief="gif nyaa~")
    async def dance(self, ctx):
        await ctx.send(
            "https://cdn.discordapp.com/attachments/779413828051664966/944648168627372133/48561229-large.gif"
        )

    @commands.hybrid_command()
    async def gumo(self, ctx):
        name = common.get_nick_or_name(ctx.author)
        await ctx.send(f"{name} {owolib.owofy('wünscht allen einen GuMo!')}")

    @commands.hybrid_command()
    async def gumi(self, ctx):
        name = common.get_nick_or_name(ctx.author)
        await ctx.send(f"{name} {owolib.owofy('wünscht allen einen Guten Mittach!')}")

    @commands.hybrid_command()
    async def guna(self, ctx):
        name = common.get_nick_or_name(ctx.author)
        await ctx.send(f"{name} {owolib.owofy('wünscht allen eine GuNa!')}")

    @commands.hybrid_command()
    async def slap(self, ctx, member: discord.Member):
        name1 = common.get_nick_or_name(ctx.author)
        name2 = common.get_nick_or_name(member)
        await ctx.send(name1 + " slaps " + name2)
        await ctx.send("https://tenor.com/view/slap-bear-slap-me-you-gif-17942299")

    @commands.hybrid_command(brief="steal an avatar")
    async def steal(self, ctx, member: discord.Member):
        await ctx.send(member.display_avatar.url)

    @commands.hybrid_command(brief="Pong is a table tennis–themed twitch arcade sports video game "
                                   "featuring simple graphics.")
    async def ping(self, ctx: commands.Context):
        await ctx.send(f":ping_pong: ping pong! (`{round(self.bot.latency * 1000)}ms`)")

    sad_words = {"trauer", "schmerz", "leid"}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        word = message.content[1:].lower()
        if message.content and message.content[0] == self.bot.command_prefix and word in self.sad_words:
            self.bot.handle_dynamic(message)
            sad_words_minus = self.sad_words - {word}
            send_word = random.choice(tuple(sad_words_minus))
            await message.channel.send(send_word)


def setup(bot):
    return bot.add_cog(SimpleCommands(bot))
