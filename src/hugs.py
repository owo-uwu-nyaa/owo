import discord
from discord.ext import commands
from pygelbooru import Gelbooru
import common


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

    @commands.command(brief="@someone <3")
    async def hug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, 'hug')
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (2 boys hugging)")
    async def bhug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, 'hug 2boys')
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (customize your hug!)")
    async def hugc(self, ctx, member: discord.Member, tag_str: str):
        gelbooru_url = await self.get_hug_gelbooru(ctx, tag_str)
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (hug someone from behind)")
    async def hug_behind(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, 'hug hug_from_behind')
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (people hugging)")
    async def ahug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, 'hug androgynous')
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (2 girls hugging)")
    async def ghug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, 'hug 2girls')
        await send_hug(ctx, member, str(gelbooru_url))
