import io
import functools as ft
from datetime import datetime, timezone, timedelta
import cgi

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
        await common.send_paginated(ctx, owolib.owofy(msg), page_length=2000)

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
        attachments = list(message.attachments)
        text = message.content
        if (not text) and attachments:
            text_from = attachments[0]
            media_type, params = cgi.parse_header(text_from.content_type)
            if media_type.startswith("text/"):
                content = io.BytesIO()
                await text_from.save(fp=content)
                try:
                    text = content.getvalue().decode(params.get("charset", "utf-8"))
                    attachments.pop(0)
                except UnicodeDecodeError:
                    # incorrect encoding declared?
                    attachments.insert(0, text_from)

        if text.startswith(self.bot.command_prefix):
            return

        # if the last message is owofied and was sent by the same author, preserve the author to not split messages
        last_message = await anext(message.channel.history(before=message, limit=1), None)
        keep_last_owauthor = (
            last_message is not None
            and datetime.now(timezone.utc) - last_message.created_at < timedelta(minutes=7)
            and last_message.webhook_id is not None
            and owo_chan.last_author == message.author.id and owo_chan.last_message == last_message.id
        )

        def update_last_owo(owo_author=None, owo_message=None):
            OwoChan.update(
                {OwoChan.last_author: owo_author and owo_author.id, OwoChan.last_message: owo_message and owo_message.id}
            ).where(
                OwoChan.channel == message.channel.id
            ).execute()

        tokens = [tok for tok in text.split(" ") if tok.strip()]
        owo_score = owolib.score(text)
        # which messages should not be uwu *rawr xd*
        nowo = bool(
            owo_score >= 1
            or not contains_alpha(text)
            or (not text and message.attachments)
            or (len(tokens) == 1 and discord_linkify_likely(tokens[0]))
        )

        # if the last message is in an owo-streak, always send from an owo-user to preserve the streak
        # but otherwise, return
        if not keep_last_owauthor and nowo:
            update_last_owo()
            return

        webhook = None
        for channel_webhook in await message.channel.webhooks():
            if channel_webhook.user == self.bot.user and channel_webhook.auth_token is not None:
                webhook = channel_webhook
                break
        if webhook is None:
            webhook = await message.channel.create_webhook(name="if you read this you're cute")

        if owo_score < 1:
            text = owolib.owofy(text)

        if keep_last_owauthor:
            author_name = last_message.author.display_name
            # in this case, no need to update DB: last_author is the same
        else:
            author_name = owolib.owofy(message.author.display_name)
        author_avatar_url = message.author.display_avatar.url
        mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)
        # as the original message is deleted, we need to re-upload the attachments
        files = []
        for attachment in attachments:
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

        # content may be at most 2000 characters
        # https://discord.com/developers/docs/resources/webhook#execute-webhook-jsonform-params
        send = ft.partial(
            common.send_paginated,
            webhook,
            page_length=2000,
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

        last_msg = (await send(text, files=files, wait=True))[-1]
        await message.delete()

        update_last_owo(owo_author=message.author, owo_message=last_msg)


def setup(bot):
    return bot.add_cog(OwO(bot))
