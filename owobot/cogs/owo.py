import io
import discord
from discord.ext import commands
from misc import owolib, common
from misc.db import OwoChan


def contains_alpha(text: str) -> bool:
    for ltr in text:
        if ltr.isalpha():
            return True
    return False


class Owo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="owofy <msg> nyaa~~")
    async def owofy(self, ctx, *, msg: str):
        owofied = owolib.owofy(msg)
        await ctx.send(f'```{common.sanitize_markdown(owofied)} ```')

    @commands.command(brief="telwlws you how owo-kawai <msg> is - scowre >= 1 is owo :3")
    async def rate(self, ctx, *, msg: str):
        score = owolib.score(msg)
        await ctx.send(f'S-Senpai ywou scwored a {score:.2f}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.webhook_id is not None:
            return
        if not OwoChan.select().where(OwoChan.channel == message.channel.id).exists():
            return
        text = message.content
        if owolib.score(text) > 1 or not contains_alpha(text) or text.startswith(self.bot.command_prefix):
            return
        webhooks = await message.channel.webhooks()
        if len(webhooks) > 0:
            webhook = webhooks[0]
        else:
            webhook = await message.channel.create_webhook(name="if you read this you're cute")
        for _ in range(0, 5):
            if owolib.score(text := owolib.owofy(text)) > 1.0:
                break
        author_name = owolib.owofy(message.author.display_name)
        author_avatar_url = message.author.avatar.url
        mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)
        # as the original message is deleted, we need to re-upload the attachments
        files = []
        for attachment in message.attachments:
            fp = io.BytesIO()
            await attachment.save(fp)
            fp.seek(0)
            file = discord.File(fp, filename=attachment.filename, description="owo", spoiler=attachment.is_spoiler())
            files.append(file)
        await webhook.send(
            content=common.sanitize_send(text),
            username=author_name,
            avatar_url=author_avatar_url,
            allowed_mentions=mentions,
            files=files
        )
        await message.delete()
