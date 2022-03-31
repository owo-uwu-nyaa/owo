import random
import re
import discord
from discord.ext import commands
from owobot.misc import common, owolib


class SimpleCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def obamamedal(self, ctx):
        await ctx.send("https://media.discordapp.net/attachments/798609300955594782/816701722818117692/obama.jpg")

    @commands.command()
    async def owobamamedal(self, ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/938102328282722345/939605208999264367/Unbenannt.png")

    @commands.command(aliases=["hewwo"])
    async def hello(self, ctx):
        await ctx.send(random.choice(["Hello", "Hello handsome :)"]))

    @commands.command(aliases=["evewyone"])
    async def everyone(self, ctx):
        await ctx.send("@everyone")

    @commands.command(brief="OwO")
    async def owo(self, ctx):
        await ctx.send(owolib.get_random_emote())

    @commands.command(brief="lena")
    async def baaa(self, ctx):
        """make $baaa appear in the help message"""
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        lambs = ["https://cdn.discordapp.com/attachments/779413828051664966/943597938687508500/unknown.png",
                 "https://external-preview.redd.it/wagY3h0C30loblI2uoR9SehYbfFvVQy9B5h3Uj8z558.jpg?auto=webp&s=bb28031f340f704158f57ae0d7cd1e6fd32607e6",
                 "https://external-preview.redd.it/lCLKqsCtHuBLiT2kGE4iBNVOjKMH5yqMawR4wQ98Ucg.jpg?auto=webp&s=ed9bfff8d26568eab73224829fb00bd0c9deda66",
                 "https://external-preview.redd.it/PXHSMB68W5TZF2TSaGju44KCR4Iu0r9XWCtyh5I6wrE.jpg?auto=webp&s=5b48fe3de0716400b927c5cc4278a1379e8defc3",
                 "https://i.redd.it/kfjickllacl51.jpg",
                 "https://external-preview.redd.it/SkZuA3VBqvnCFcSUDhmmEIMfFuk_o6TeqNvp9Jlw68E.jpg?auto=webp&s=31dfd9febdaadbe9f33555127fc27cd257b9da64"]
        # TODO this is very broken if the prefix changes
        if re.match(r"^\$baaa+$", message.content):
            await message.channel.send("<@898152253330972672>")
            await message.channel.send(random.choice(lambs))

    @commands.command(brief="gif nyaa~")
    async def dance(self, ctx):
        await ctx.send(
            "https://cdn.discordapp.com/attachments/779413828051664966/944648168627372133/48561229-large.gif")

    @commands.command()
    async def gumo(self, ctx):
        name = common.get_nick_or_name(ctx.author)
        await ctx.send(name + " " + owolib.owofy(" wünscht allen einen GuMo!"))

    @commands.command()
    async def gumi(self, ctx):
        name = common.get_nick_or_name(ctx.author)
        await ctx.send(name + " " + owolib.owofy(" wünscht allen einen Guten Mittach!"))

    @commands.command()
    async def guna(self, ctx):
        name = common.get_nick_or_name(ctx.author)
        await ctx.send(name + " " + owolib.owofy(" wünscht allen eine GuNa!"))

    def gen_row(self, maxlen: int, cur_row: int):
        ltr = chr(ord('A') + cur_row)
        opad = maxlen - cur_row - 1
        if cur_row == 0:
            return f"{'.' * opad}{ltr}{'.' * opad}"
        return f"{'.' * opad}{ltr}{'.' * ((cur_row * 2) - 1)}{ltr}{'.' * opad}"

    @commands.command()
    async def diamond(self, ctx, nrows: int):
        if nrows > 22:
            await ctx.send(f"{owolib.get_random_sorry()}, thiws is too mwuch fow me to take nyaaa~")
            return
        if nrows < 1:
            await ctx.send(f"{owolib.get_random_sorry()}, thiws is nwot enough fow me, give me more nyaaa~")
            return
        result = []
        for i in range(0, nrows - 1):
            result.append(self.gen_row(nrows, i))
        for i in range(nrows - 1, -1, -1):
            result.append(self.gen_row(nrows, i))
        diamond = '\n'.join(result)
        await ctx.send(f"```\n{diamond}\n```")

    @commands.command()
    async def slap(self, ctx, member: discord.Member):
        name1 = common.get_nick_or_name(ctx.author)
        name2 = common.get_nick_or_name(member)
        await ctx.send(name1 + " slaps " + name2)
        await ctx.send("https://tenor.com/view/slap-bear-slap-me-you-gif-17942299")

    @commands.command(brief="steal an avatar")
    async def steal(self, ctx, member: discord.Member):
        await ctx.send(member.avatar.url)


def setup(bot):
    bot.add_cog(SimpleCommands(bot))