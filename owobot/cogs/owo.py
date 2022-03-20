from discord.ext import commands
from misc import owolib, common


def contains_alpha(str: str) -> bool:
    for ltr in str:
        if ltr.isalpha():
            return True
    return False

class Owo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="owofy <msg> nyaa~~")
    async def owofy(self, ctx, *, msg: str):
        owofied = owolib.owofy(msg)
        await ctx.send(f'```{common.sanitize(owofied)} ```')

    @commands.command(brief="telwlws you how owo-kawai <msg> is - scowre >= 1 is owo :3")
    async def rate(self, ctx, *, msg: str):
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
            if owo_score < 1 and contains_alpha(msg):
                owofied = owolib.owofy(msg)
                #   await message.channel.send(
                #       f'{owolib.get_random_sorry()} <@{message.author.id}> youw seem to nwot hav owofied ywour text.. h-here lwet me show you:\n```\n{common.sanitize(owofied)}\n```')
                #   ^ on top: previous version of owosend
                #   🥺 on bottom: funny webhook things, relevant pycord docs: https://docs.pycord.dev/en/master/api.html?highlight=webhook#discord.Webhook
                #   this should be self-documenting
                webhook = message.channel.webhooks()[0]
                if webhook is None:
                    webhook = await message.channel.create_webhook('if u read this ur gay')
                await webhook.send(
                    content = common.sanitize(owofied),
                    username = owolib.owofy(message.author.display_name),
                    avatar_url = message.author.avatar.url)
