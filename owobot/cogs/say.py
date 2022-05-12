# Cog stolen and modified from https://github.com/janin-s/ki_pybot/blob/c9f9c7c55c51864eb0aaff9b4dbe704773263567/lib/cogs/say.py
import io

import discord
import discord.ext
from discord.ext.commands import Cog, command, Context

from owobot.misc import common


class Say(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("say ready")

    @command()
    async def say(self, ctx: Context, member: discord.Member, content):
        """'!say [mention | user_id] content' creates message impersonating the user"""
        guild_webhooks: list[discord.Webhook] = await ctx.guild.webhooks()
        webhooks_filtered: list[discord.Webhook] = [w for w in guild_webhooks if str(ctx.channel.id) in w.name]
        if not webhooks_filtered:
            webhook: discord.Webhook = await ctx.channel.create_webhook(name=f'say-cmd-hook-{ctx.channel.id}')
        else:
            webhook: discord.Webhook = webhooks_filtered[0]

        files = []
        for attachment in ctx.message.attachments:
            fp = io.BytesIO()
            await attachment.save(fp)
            fp.seek(0)
            file = discord.File(fp, filename=attachment.filename, description="owo", spoiler=attachment.is_spoiler())
            files.append(file)

        await ctx.message.delete()

        mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)
        await webhook.send(content=common.sanitize_send(content),
                           username=common.get_nick_or_name(member),
                           avatar_url=member.avatar.url,
                           allowed_mentions=mentions,
                           files=files)

def setup(bot):
    bot.add_cog(Say(bot))
