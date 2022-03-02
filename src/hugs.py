import discord
from discord.ext import commands
from pygelbooru import Gelbooru
import common
import owolib


async def send_hug(ctx: object, member: object, img_url: str) -> None:
    await ctx.send(f'{common.get_nick_or_name(ctx.author)} sends you a hug, {common.get_nick_or_name(member)}')
    await ctx.send(img_url)


class Hugs(commands.Cog):

    def __init__(self, bot):
        # TODO is this even threadsafe?
        self.gelbooru = Gelbooru()
        self.bot = bot

    # penguin pics
    # random.choice(["https://tenor.com/view/chibird-penguin-hug-gif-14248948", "https://tenor.com/view/cuddle-group-group-hug-friends-penguin-gif-13295520"])
    async def get_hug_gelbooru(self, ctx, tags):
        tags = tags.split(' ')
        tags.append('hug')
        blocklist = ['loli', 'futanari', 'shota']
        if ctx.channel.id != 945070395093041195:
            blocklist += ['rating:explicit', 'nude']
            tags.append('rating:safe')
        result = await self.gelbooru.random_post(tags=tags, exclude_tags=blocklist)
        return result

    """Nils: bonking is basically a hug"""
    @commands.command(brief="bonk")
    async def bonk(self, ctx, member: discord.Member):
        name = common.get_nick_or_name(ctx.author)
        other = common.get_nick_or_name(member)
        await ctx.send(f"{name} {owolib.owofy('bonkt')} {other} <:pingbonk:940280394736074763>")

    @commands.command(brief="@someone <3 (2 boys hugging)")
    async def bhug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, 'hug 2boys')
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (customize your hug!)", aliases=["hugc"])
    async def hug(self, ctx, member: discord.Member, *tags: str):
        #convert tags to a space separated string, as thats what get_hug_gelbooru expects
        gelbooru_url = await self.get_hug_gelbooru(ctx, " ".join(tags))
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (people hugging)")
    async def ahug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, 'hug androgynous')
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (2 girls hugging)")
    async def ghug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, 'hug 2girls')
        await send_hug(ctx, member, str(gelbooru_url))
