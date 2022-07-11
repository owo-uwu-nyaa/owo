import random

import discord
from discord.ext import commands

from owobot.misc import common, owolib


class SimpleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def obamamedal(self, ctx):
        await ctx.send(
            "https://media.discordapp.net/attachments/798609300955594782/816701722818117692/obama.jpg"
        )

    @commands.command()
    async def owobamamedal(self, ctx):
        await ctx.send(
            "https://cdn.discordapp.com/attachments/938102328282722345/939605208999264367/Unbenannt.png"
        )

    @commands.command(aliases=["hewwo"])
    async def hello(self, ctx):
        await ctx.send(random.choice(["Hello", "Hello handsome :)"]))

    @commands.command(aliases=["evewyone"])
    async def everyone(self, ctx):
        await ctx.send("@everyone")

    @commands.command(brief="OwO")
    async def owo(self, ctx):
        await ctx.send(owolib.get_random_emote())

    @commands.command(brief="gif nyaa~")
    async def dance(self, ctx):
        await ctx.send(
            "https://cdn.discordapp.com/attachments/779413828051664966/944648168627372133/48561229-large.gif"
        )

    @commands.command()
    async def gumo(self, ctx):
        name = common.get_nick_or_name(ctx.author)
        await ctx.send(f"{name} {owolib.owofy('wünscht allen einen GuMo!')}")

    @commands.command()
    async def gumi(self, ctx):
        name = common.get_nick_or_name(ctx.author)
        await ctx.send(f"{name} {owolib.owofy('wünscht allen einen Guten Mittach!')}")

    @commands.command()
    async def guna(self, ctx):
        name = common.get_nick_or_name(ctx.author)
        await ctx.send(f"{name} {owolib.owofy('wünscht allen eine GuNa!')}")

    def gen_row(self, maxlen: int, cur_row: int):
        ltr = chr(ord("A") + cur_row)
        opad = maxlen - cur_row - 1
        if cur_row == 0:
            return f"{'.' * opad}{ltr}{'.' * opad}"
        return f"{'.' * opad}{ltr}{'.' * ((cur_row * 2) - 1)}{ltr}{'.' * opad}"

    @commands.command()
    async def diamond(self, ctx, nrows: int):
        if nrows > 22:
            await ctx.send(
                f"{owolib.get_random_sorry()}, thiws is too mwuch fow me to take nyaaa~"
            )
            return
        if nrows < 1:
            await ctx.send(
                f"{owolib.get_random_sorry()}, thiws is nwot enough fow me, give me more nyaaa~"
            )
            return
        result = []
        for i in range(0, nrows - 1):
            result.append(self.gen_row(nrows, i))
        for i in range(nrows - 1, -1, -1):
            result.append(self.gen_row(nrows, i))
        diamond = "\n".join(result)
        await ctx.send(f"```\n{diamond}\n```")

    @commands.command()
    async def slap(self, ctx, member: discord.Member):
        name1 = common.get_nick_or_name(ctx.author)
        name2 = common.get_nick_or_name(member)
        await ctx.send(name1 + " slaps " + name2)
        await ctx.send("https://tenor.com/view/slap-bear-slap-me-you-gif-17942299")

    @commands.command(brief="steal an avatar")
    async def steal(self, ctx, member: discord.Member):
        await ctx.send(member.display_avatar.url)

    sad_words = {"trauer", "schmerz", "leid"}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        word = message.content[1:].lower()
        if message.content[0] == self.bot.command_prefix and word in self.sad_words:
            sad_words_minus = self.sad_words - {word}
            send_word = random.choice(tuple(sad_words_minus))
            await message.channel.send(send_word)


def setup(bot):
    bot.add_cog(SimpleCommands(bot))
