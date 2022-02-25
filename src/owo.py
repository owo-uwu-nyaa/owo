import random

from discord.ext import commands
import owolib
import uwu_data


class Owo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="owofy <msg> nyaa~~")
    async def owofy(self, ctx, *, msg: str):
        owofied = owolib.owofy(msg)
        await ctx.send(f'```{owofied.replace("`", "")} ```')

    @commands.command(brief="telwlws you how owo-kawai <msg> is - scowre >= 1 is owo :3")
    async def rate(self, ctx, msg: str):
        score = owolib.score(msg)
        await ctx.send(f'S-Senpai ywou scwored a {score:.2f}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.channel.id == 937306121901850684:
            words = message.content.split()
            nmsg = []
            for word in words:
                if not word.startswith("http") and not (word[0] == "<" and word[-1] == ">"):
                    nmsg.append(word)
            msg = " ".join(nmsg)
            owo_score = owolib.score(msg)
            is_only_alpha = True
            for ltr in msg:
                if ltr.isalpha():
                    is_only_alpha = False
            if owo_score < 1 and not is_only_alpha:
                answer = owolib.owofy(msg)
                await message.channel.send(
                    f'{random.choice(uwu_data.sowwy)} <@{message.author.id}> youw seem to nwot hav owofied ywour text.. h-here lwet me show you:\n```{answer.replace("`", "")} ```')