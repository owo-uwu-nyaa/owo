import random

import discord
from discord.ext import commands
from misc import common
from furl import furl
from misc.db import NsflChan
import json
import aiohttp


def _sparkles_or_none(text: str) -> str:
    return "✨" if len(text) < 1 else text


class E621(commands.Cog):
    _create_basefurl = furl("https://e621.net/posts.json/").copy

    def __init__(self, bot, config):
        self.config = config
        self.bot = bot
        self.posts = []

    async def _get_posts(self, url):
        async with aiohttp.ClientSession(headers={"User-Agent": "owo"}) as sess:
            req = await sess.get(url)
            posts = json.loads(await req.text())
            return posts["posts"]

    async def _pretty_send(self, ctx, post):
        embed = discord.Embed()
        embed.set_image(url=post["file"]["url"])
        tags = post["tags"]
        embed.add_field(name="species", value=_sparkles_or_none(" ".join(tags["species"])), inline=True)
        embed.add_field(name="char(s)", value=_sparkles_or_none(" ".join(tags["character"])), inline=True)
        embed.add_field(name="artist(s)", value=_sparkles_or_none(" ".join(tags["artist"])), inline=True)
        embed.add_field(name="general tags", value=_sparkles_or_none(" ".join(tags["general"][:1023])), inline=True)
        embed.set_footer(text=post["description"][:1023])
        await ctx.send(embed=embed)

    async def cog_check(self, ctx):
        res = NsflChan.select().where(NsflChan.channel == ctx.channel.id).exists()
        if not res:
            await common.react_failure(ctx)
        return res

    @commands.group()
    async def e(self, ctx):
        pass

    @e.command(name="random", brief="random image from e621", aliases=["r"])
    async def e_random(self, ctx):
        if len(self.posts) == 0:
            self.posts = await self._get_posts(self._create_basefurl().add({"tags": "order:random"}).url)
        await self._pretty_send(ctx, self.posts.pop())

    @e.command(name="tags", brief="tags!", aliases=["t"])
    async def e_tag(self, ctx, *tags: str):
        tags = ["order:random"] + list(tags)
        f = self._create_basefurl().add({"tags": " ".join(tags), "limit": "1"})
        posts = await self._get_posts(f.url)
        if len(posts) == 0:
            await common.react_empty(ctx)
            return
        post = posts[0]
        await self._pretty_send(ctx, post)
