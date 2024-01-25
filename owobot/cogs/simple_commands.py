import asyncio
import io
import random
import re
import functools as ft
import socket

from urllib.parse import urlparse, parse_qs, urlencode

import discord
import aiohttp
from wand.image import Image
from dhash import dhash_int
from discord.ext import commands
from discord import app_commands

from owobot.misc import common, owolib, interactions, discord_emoji, bottom
from owobot.misc.database import EvilTrackingParameter, MediaDHash, ForceEmbed
from owobot.owobot import OwOBot

def get_urls_in_message(message):
    urls = re.findall(r'(https?://\S+)', message.content)
    return urls

async def clear_links(urls=None):
    cringe_urls = []
    for url in urls:
        new_url = None

        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        evil = False

        params = parse_qs(parsed_url.query)
        new_params = dict.copy(params)
        for key in params.keys():
            if EvilTrackingParameter.get_or_none((EvilTrackingParameter.url == domain) & (EvilTrackingParameter.tracking_parameter == key)):
                new_params.pop(key)
                evil = True

        if evil:
            parsed_url = parsed_url._replace(query=urlencode(new_params, doseq=True))
            new_url = True

        nonembeddable_url = ForceEmbed.get_or_none(ForceEmbed.url == domain)
        if nonembeddable_url:
            parsed_url = parsed_url._replace(netloc=nonembeddable_url.new_url)
            new_url = True

        if new_url:
            cringe_urls.append((url, parsed_url.geturl()))

    return cringe_urls

class SimpleCommands(interactions.ContextMenuCog):
    def __init__(self, bot: OwOBot):
        self.bot = bot
        asyncio.run(self.run_anon_server())
        super().__init__()


    async def send_anon_message(self, r, _):
        text = r.readline()
        channel = self.bot.config.anon_chan
        guild = self.bot.config.anon_guild
        anon_channel = self.bot.get_guild(guild).get_channel(channel)
        await anon_channel.send(text)

    async def run_anon_server(self):
        port = self.bot.config.anon_port
        server = await asyncio.start_server(self.send_anon_message, 'localhost', port)
        async with server:
            await server.serve_forever()

    @interactions.context_menu_command(name="Clear links")
    async def remove_tracking(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.send_message('Looking for evil links :3', ephemeral=True)
        cringe_urls = await clear_links(get_urls_in_message(message))
        if len(cringe_urls) == 0:
            await interaction.edit_original_response(content="I found nothing wrong with this message. Maybe consider using `add_evil_parameter` or `add_embed_url`")
        else:
            await message.add_reaction(discord_emoji.get_unicode_emoji("rotating_light"))
            await message.reply("SHAME. I've cleaned the links in your message.\n" + "\n".join(map(lambda x: x[1], cringe_urls)), mention_author=True)


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

    @commands.hybrid_command()
    async def bottom(self, ctx, text):
        result = ""
        try:
            result = bottom.to_bottom(text)
        except Exception as e:
            result = e
        finally:
            await ctx.send(result)

    @commands.hybrid_command()
    async def unbottom(self, ctx, text):
        result = ""
        try:
            result = bottom.from_bottom(text)
        except Exception as e:
            result = e
        finally:
            await ctx.send(result)

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

    async def recreate_message(self, message, content, reply):
        files = []
        attachments = list(message.attachments)

        for attachment in attachments:
            fp = io.BytesIO()
            await attachment.save(fp)
            fp.seek(0)
            file = discord.File(
                fp,
                filename=attachment.filename,
                description=attachment.description or "",
                spoiler=attachment.is_spoiler(),
            )
            files.append(file)

        webhook = None
        for channel_webhook in await message.channel.webhooks():
            if channel_webhook.user == self.bot.user and channel_webhook.auth_token is not None:
                webhook = channel_webhook
                break
        if webhook is None:
            webhook = await message.channel.create_webhook(name="if you read this you're cute")

        reply_embed = (
            await common.message_as_embedded_reply(
                await message.channel.fetch_message(message.reference.message_id)
            )
            if message.reference
            else None
        )

        # content may be at most 2000 characters
        # https://discord.com/developers/docs/resources/webhook#execute-webhook-jsonform-params
        send = ft.partial(
            common.send_paginated,
            webhook,
            page_length=2000,
            username=message.author.display_name,
            avatar_url=message.author.display_avatar.url,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
        )
        # send the "reply" and the actual message separately,
        # which lets Discord automatically (re)generate the embeds from the message body in the second message
        # (there is no way to send anything except 'rich' embeds through the API)

        if reply_embed is not None:
        # wait=True so messages don't get sent out-of-order
            await send(embed=reply_embed, wait=True)
        await send(content, files=files, wait=True)


    async def clear_message(self, message, urls=None, delete=False):
        cringe_urls = await clear_links(urls or get_urls_in_message(message))

        content = message.content if len(cringe_urls) > 0 else None
        for url, new_url in cringe_urls:
            content = content.replace(url, new_url)

        if content is None:
            return
        
        await self.recreate_message(message, content, not delete)
        if delete:
            await message.delete()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author == self.bot.user or message.webhook_id is not None:
            return

        urls = get_urls_in_message(message)
        if self.bot.config.repost_shaming and urls:
            urls += [a.url for a in message.attachments]
            for url in urls:
                await self.check_url_for_repost(url, message)

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

        await self.clear_message(message, urls=urls, delete=True)


def setup(bot):
    return bot.add_cog(SimpleCommands(bot))
