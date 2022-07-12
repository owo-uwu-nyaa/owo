import io
import discord
import functools as ft
from discord.ext import commands
from owobot.misc import owolib, common
from owobot.misc.database import OwoChan


def contains_alpha(text: str) -> bool:
    for ltr in text:
        if ltr.isalpha():
            return True
    return False


class OwO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="owofy <msg> nyaa~~")
    async def owofy(self, ctx, *, msg: str):
        owofied = owolib.owofy(msg)
        await ctx.send(f"```{common.sanitize_markdown(owofied)} ```")

    @commands.command(
        brief="telwlws you how owo-kawai <msg> is - scowre >= 1 is owo :3"
    )
    async def rate(self, ctx, *, msg: str):
        score = owolib.score(msg)
        await ctx.send(f"S-Senpai y-y-you scowed a {score:.2f}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if message.author == self.bot.user or message.webhook_id is not None:
            return
        if not OwoChan.select().where(OwoChan.channel == message.channel.id).exists():
            return
        text = message.content
        if (
            owolib.score(text) > 1
            or not contains_alpha(text)
            or text.startswith(self.bot.command_prefix)
        ):
            return
        webhooks = await message.channel.webhooks()
        if len(webhooks) > 0:
            webhook = webhooks[0]
        else:
            webhook = await message.channel.create_webhook(
                name="if you read this you're cute"
            )
        for _ in range(5):
            if owolib.score(text := owolib.owofy(text)) > 1.0:
                break
        text = common.sanitize_send(text)
        if len(text) > 2000:
            # content may be at most 2000 characters
            # https://discord.com/developers/docs/resources/webhook#execute-webhook-jsonform-params
            return
        author_name = owolib.owofy(message.author.display_name)
        author_avatar_url = message.author.display_avatar.url
        mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)
        # as the original message is deleted, we need to re-upload the attachments
        files = []
        for attachment in message.attachments:
            fp = io.BytesIO()
            await attachment.save(fp)
            fp.seek(0)
            file = discord.File(
                fp,
                filename=attachment.filename,
                description="owo",
                spoiler=attachment.is_spoiler(),
            )
            files.append(file)
        # webhooks don't support real replies
        reply_embed = (
            await common.message_as_embedded_reply(
                await message.channel.fetch_message(message.reference.message_id)
            )
            if message.reference
            else None
        )

        send = ft.partial(
            webhook.send,
            username=author_name,
            avatar_url=author_avatar_url,
            allowed_mentions=mentions,
        )
        # send the "reply" and the actual message separately,
        # which lets Discord automatically (re)generate the embeds from the message body in the second message
        # (there is no way to send anything except 'rich' embeds through the API)
        if reply_embed is not None:
            await send(embed=reply_embed)
        await send(content=text, files=files)
        await message.delete()


def setup(bot):
    bot.add_cog(OwO(bot))
