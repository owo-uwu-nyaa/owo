import io
import functools as ft
from datetime import datetime, timezone, timedelta

import discord
from discord.ext import commands

from owobot.misc import owolib, common
from owobot.misc.common import anext, discord_linkify_likely
from owobot.misc.database import OwoChan

from typing import List, Tuple


def contains_alpha(text: str) -> bool:
    return any(char.isalpha() for char in text)


class OwO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(brief="owofy <msg> nyaa~~")
    async def owofy(self, ctx, *, msg: str):
        owofied = owolib.owofy(msg)
        await ctx.send(f"```{common.sanitize_markdown(owofied)} ```")

    @commands.hybrid_command(
        brief="telwlws you how owo-kawai <msg> is - scowre >= 1 is owo :3"
    )
    async def rate(self, ctx, *, msg: str):
        score = owolib.score(msg)
        await ctx.send(f"S-Senpai y-y-you scowed a {score:.2f}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user or message.webhook_id is not None:
            return
        owo_chan = OwoChan.select().where(OwoChan.channel == message.channel.id).get_or_none()
        if not owo_chan:
            return
        text = message.content

        if text.startswith(self.bot.command_prefix):
            return

        # if the last message is owofied and was sent by the same author, preserve the author to not split messages
        last_message = await anext(message.channel.history(before=message, limit=1), None)
        keep_last_owauthor = (
            last_message is not None
            and datetime.now(timezone.utc) - last_message.created_at < timedelta(minutes=7)
            and last_message.webhook_id is not None
            and owo_chan.last_author == message.author.id and owo_chan.last_message == message.id
        )

        def update_last_owo(owo_author=None, owo_message=None):
            OwoChan.update(
                {OwoChan.last_author: owo_author and owo_author.id, OwoChan.last_message: owo_message and owo_message.id}
            ).where(
                OwoChan.channel == message.channel.id
            ).execute()

        tokens = [tok for tok in text.split(" ") if tok.strip()]
        # which messages should not be uwu *rawr xd*
        nowo = (
            owolib.score(text) >= 1
            or not contains_alpha(text)
            or (not text and message.attachments)
            or (len(tokens) == 1 and discord_linkify_likely(tokens[0]))
        )

        # if the last message is in an owo-streak, always send from an owo-user to preserve the streak
        if not keep_last_owauthor and nowo:
            update_last_owo()
            return

        webhook = None
        for channel_webhook in await message.channel.webhooks():
            if channel_webhook.user == self.bot.user and channel_webhook.auth_token is not None:
                webhook = channel_webhook
        if webhook is None:
            webhook = await message.channel.create_webhook(name="if you read this you're cute")

        if not nowo:
            for _ in range(5):
                if owolib.score(text := owolib.owofy(text)) > 1.0:
                    break
        text = common.sanitize_send(text)
        if len(text) > 2000:
            # content may be at most 2000 characters
            # https://discord.com/developers/docs/resources/webhook#execute-webhook-jsonform-params
            update_last_owo()
            return

        if keep_last_owauthor:
            author_name = last_message.author.display_name
            # in this case, no need to update DB: last_author is the same
        else:
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
            # wait=True so messages don't get sent out-of-order
            await send(embed=reply_embed, wait=True)
        last_msg = await send(content=text, files=files, wait=True)
        await message.delete()

        update_last_owo(owo_author=message.author, owo_message=last_msg)


def setup(bot):
    return bot.add_cog(OwO(bot))
