import asyncio
import random
import re

from urllib.parse import urlparse

import discord
import aiohttp
from wand.image import Image
from dhash import dhash_int
from discord.ext import commands

from owobot.misc import common, owolib
from owobot.misc.database import MediaDHash, ForceEmbed
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
        if reaction.emoji == "🤡" and reaction.message.author == self.bot.user and reaction.message.content.startswith("♻️"):
            message = reaction.message
            urls = re.findall(r'(https?://\S+)', message.content)
            # extract guild, channel and message id from url
            guild_id, channel_id, message_id = urls[1].split("/")[-3:]
            print(guild_id, channel_id, message_id)
            orig_post = MediaDHash.select().where(
                (MediaDHash.guild == int(guild_id)) &
                (MediaDHash.channel == int(channel_id)) &
                (MediaDHash.message == int(message_id))).first()
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
    async def send_shame_message(message, orig_post, url):
        shame_message = f"♻️ Hewooo! I have already seen the same content as <{url}> in message https://discord.com/channels/{orig_post.guild}/{orig_post.channel}/{orig_post.message} "
        if orig_post.orig_url != url:
            shame_message += f"\nunder the URL <{orig_post.orig_url}> "
        shame_message += "\n If you think this content is cute and shamed in error, react with 🤡"
        await message.reply(shame_message)

    @staticmethod
    async def insert_hash_into_db(message, dhash, url):
        MediaDHash.create(hash=dhash, guild=message.guild.id, channel=message.channel.id,
                          message=message.id, orig_url=url,
                          whitelisted=0)

    async def check_url_for_repost(self, url, message: discord.Message):
        # async get request
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as r:
                try:
                    if r.status != 200:
                        return
                    content = await r.content.read()
                    image = Image(blob=content)
                    dhash = dhash_int(image, 4)
                    orig_post = MediaDHash.select().where((MediaDHash.hash == dhash) & (
                            MediaDHash.guild == message.guild.id)).first()
                    if not orig_post:
                        await SimpleCommands.insert_hash_into_db(message, dhash, url)
                        return
                    if orig_post.whitelisted > 1:
                        return
                    # check if the original message still exists
                    try:
                        await self.bot.get_guild(orig_post.guild).get_channel(orig_post.channel).fetch_message(
                            orig_post.message)
                    except discord.NotFound:
                        orig_post.delete_instance()
                        await SimpleCommands.insert_hash_into_db(message, dhash, url)
                        return
                    await SimpleCommands.send_shame_message(message, orig_post, url)
                except Exception as ex:
                    print(ex)
                    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        urls = re.findall(r'(https?://\S+)', message.content)
        urls += [a.url for a in message.attachments]
        if self.bot.config.repost_shaming and urls:
            for url in urls:
                await self.check_url_for_repost(url, message)

        embeddable_urls = []
        for url in urls:
            domain = urlparse(url).netloc
            print(domain)
            query = ForceEmbed.get_or_none(ForceEmbed.url == domain)
            print(query)
            if query:
                x = url.replace(domain, query.new_url)
                print(x)
                embeddable_urls.append(x)
        
        if len(embeddable_urls) > 0:
            await message.channel.send("\n".join(embeddable_urls))

        if re.match("\w+(\w)\\1+$", message.content):
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
