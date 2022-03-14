import discord
from discord.ext import commands
from peewee import SQL
from pygelbooru import Gelbooru
from misc import common, owolib
from misc.common import is_owner
from misc.db import NsflChan, HugShort


async def send_hug(ctx, member, img_url: str) -> None:
    await ctx.send(f"{common.get_nick_or_name(ctx.author)} sends you a hug, {common.get_nick_or_name(member)}")
    await ctx.send(img_url)

def tags_to_str(iterable):
    return "_ _\n" + "\n".join(map(lambda x: f"`{x.key} | {x.val}`", iterable))

class Hugs(commands.Cog):

    def __init__(self, bot, config):
        self.gelbooru = Gelbooru()
        self.bot = bot

    # penguin pics
    # random.choice(["https://tenor.com/view/chibird-penguin-hug-gif-14248948", "https://tenor.com/view/cuddle-group-group-hug-friends-penguin-gif-13295520"])
    async def get_hug_gelbooru(self, ctx, tags):
        tags = tags.split(" ")
        tags.append("hug")
        blocklist = ["loli", "futanari", "shota"]
        if not NsflChan.select().where(NsflChan.channel == ctx.channel.id).exists():
            blocklist += ["rating:explicit", "nude"]
            tags.append("rating:safe")
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
        gelbooru_url = await self.get_hug_gelbooru(ctx, "hug 2boys")
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (customize your hug!)", aliases=["hugc"])
    async def hug(self, ctx, member: discord.Member, *tags: str):
        # convert tags to a space separated string, as thats what get_hug_gelbooru expects
        gelbooru_url = await self.get_hug_gelbooru(ctx, " ".join(tags))
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (people hugging)")
    async def ahug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, "hug androgynous")
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (2 girls hugging)")
    async def ghug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, "hug 2girls")
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (2 girls hugging)")
    async def ghug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, "hug 2girls")
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="Use the tag shorthands uwu :)")
    async def h(self, ctx, member: discord.Member, *short: str):
        tags = ""
        if len(short) > 0:
            query = HugShort.select().where(HugShort.key.in_(list(short[0])))
            tags = " ".join(map(lambda x: str(x.val), list(query))) + " " + " ".join(short[1:])
        gelbooru_url = await self.get_hug_gelbooru(ctx, tags)
        await send_hug(ctx, member, str(gelbooru_url))

    @commands.group()
    async def hugconfigure(self, ctx):
        pass

    @hugconfigure.command(brief="explain what a short str is translated to")
    async def explain(self, ctx, short: str):
        query = HugShort.select().where(HugShort.key.in_(list(short)))
        await ctx.channel.send(tags_to_str(query))

    @hugconfigure.command(brief="list tag short")
    async def list(self, ctx):
        query = HugShort.select()
        await ctx.channel.send(tags_to_str(query))

    @commands.check(is_owner)
    @hugconfigure.command(brief="add a tag short")
    async def add(self, ctx, short: str, tag: str):
        if len(short) == 1:
            try:
                HugShort.create(key=short, val=tag)
                await common.react_success(ctx)
            except:
                await common.react_failure(ctx)

    @commands.check(is_owner)
    @hugconfigure.command(brief="rm a tag short")
    async def rm(self, ctx, short: str):
        try:
            HugShort.delete().where(HugShort.key == short).execute()
            await common.react_success(ctx)
        except:
            await common.react_failure(ctx)
