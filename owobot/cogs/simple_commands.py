import asyncio
import random
import re
from hashlib import sha256

import discord
import aiohttp
from discord.ext import commands

from owobot.misc import common, owolib
from owobot.misc.database import UrlContentHashes
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

    @commands.hybrid_command(brief="Purges up to n : [1,50] messages")
    async def purge(self, ctx, n):
        n = int(n)
        if n < 1 or n >= 50:
            return

        msg = await ctx.send(f"Deleting {n} message(s)...")
        deleted = await ctx.channel.purge(limit=int(n), bulk=True, check=lambda m: m != msg and m != ctx.message)
        await msg.edit(content=f'Sucessfully deleted {len(deleted)} message(s)')

    @commands.hybrid_command(brief="Pong is a table tennis–themed twitch arcade sports video game "
                                   "featuring simple graphics.")
    async def ping(self, ctx: commands.Context):
        await ctx.send(f":ping_pong: ping pong! (`{round(self.bot.latency * 1000)}ms`)")

    sad_words = {"trauer", "schmerz", "leid"}

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if reaction.emoji == "🤡":
            message = reaction.message
            urls = re.findall(r'(https?://\S+)', message.content)
            orig_post = UrlContentHashes.select().where(UrlContentHashes.orig_message == urls[1]).first()
            if orig_post:
                orig_post.whitelisted += 1
                orig_post.save()
            if orig_post.whitelisted > 1:
                await message.edit(content="Sowwy, i will leave you alone :3")
                await asyncio.sleep(10)
                await message.delete()

        if reaction.emoji != "🏓":
            return
        if user == self.bot.user:
            return
        await reaction.message.channel.send(f":ping_pong: pong! (`{round(self.bot.latency * 1000)}ms`)")


    @staticmethod
    async def check_url_for_repost(url, message: discord.Message):
        # async get request
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as r:
                if r.status != 200:
                    return
                content = await r.content.read()
                sha_hash = sha256(content)
                orig_post = UrlContentHashes.select().where((UrlContentHashes.hash == sha_hash.hexdigest()) & (UrlContentHashes.guild == message.guild.id)).first()
                if orig_post:
                    if orig_post.whitelisted > 1:
                        return
                    shame_message = f"♻️ Hewooo! I have already seen the same content as <{url}> in message {orig_post.orig_message} "
                    if orig_post.orig_url != url:
                        shame_message += f"under the URL {orig_post.orig_url})"
                    shame_message += "\n If you think this content is cute and shamed in error, react with 🤡"
                    await message.reply(shame_message)
                else:
                    print(message.jump_url)
                    UrlContentHashes.create(hash=sha_hash.hexdigest(), guild=message.guild.id, orig_url=url,
                                            orig_message=message.jump_url, whitelisted=0)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        urls = re.findall(r'(https?://\S+)', message.content)
        urls += [a.url for a in message.attachments]
        print(urls)
        if self.bot.config.repost_shaming and urls:
            for url in urls:
                await self.check_url_for_repost(url, message)

        if re.match("[\w]+(\w)\\1+$", message.content):
            c_channel = discord.utils.get(message.guild.text_channels, name=message.channel.name)
            messages = [m async for m in c_channel.history(limit=2)]

            if len(messages) > 1 and messages[1].content == message.content[:-1]:
                await message.channel.send(message.content + message.content[-1])

        word = message.content[1:].lower()
        if message.content and message.content[0] == self.bot.command_prefix and word in self.sad_words:
            self.bot.handle_dynamic(message)
            sad_words_minus = self.sad_words - {word}
            send_word = random.choice(tuple(sad_words_minus))
            await message.channel.send(send_word)


def setup(bot):
    return bot.add_cog(SimpleCommands(bot))
