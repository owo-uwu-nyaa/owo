import re
import threading
import discord
from discord.ext import commands
import pyspark.sql.functions as F
from recordclass import RecordClass
from emoji import UNICODE_EMOJI_ENGLISH
from typing import List, Dict
from owobot.misc.common import Variadic


class GalleryState(RecordClass):
    idx: int
    msg_id: int
    chan_id: int
    msg: discord.Message
    urls: List[str]
    embed: discord.Embed


class Gallery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.spark_lock = threading.Lock()
        self.df_attachments = bot.config.datalake.get_df("attachments")
        self.df_react = bot.config.datalake.get_df("react")
        self.gallery_by_auth: Dict[int, GalleryState] = {}
        self.gallery_by_msg: Dict[int, GalleryState] = {}

    @commands.hybrid_command(brief="see a gallery with all images you reacted to")
    async def gallery(self, ctx, args: Variadic):
        emotes = []
        channels = []
        for arg in args:
            if re.match(r"<a?:[^:<>@*~]+:\d+>", arg) or arg in UNICODE_EMOJI_ENGLISH:
                emotes.append(arg)
            elif re.match(r"<#\d+>", arg):
                channels.append(int(re.search(r"\d+", arg).group(0)))
        df_reacted = self.df_react
        df_pics = self.df_attachments
        if len(emotes) > 0:
            df_reacted = df_reacted.filter(F.col("emoji").isin(emotes))
        if len(channels) > 0:
            df_pics = df_pics.filter(F.col("channel_id").isin(channels))
        df_reacted = df_reacted.filter(
            (F.col("added") == True) & (F.col("author_id") == ctx.author.id)
        ).select("msg_id")
        df_pics = df_pics.select("msg_id", "attachment")
        df_wanted_pics = (
            df_reacted.join(df_pics, "msg_id").drop("msg_id").dropDuplicates().collect()
        )
        embed = discord.Embed()
        embed.set_image(url=df_wanted_pics[0][0])
        embed.set_footer(text=f"1/{len(df_wanted_pics)}")
        sent = await ctx.send(embed=embed)
        await sent.add_reaction(self.config.left_emo)
        await sent.add_reaction(self.config.right_emo)
        state = GalleryState(
            idx=0,
            msg_id=sent.id,
            chan_id=ctx.channel.id,
            urls=df_wanted_pics,
            embed=embed,
            msg=sent,
        )
        oldstate = self.gallery_by_auth.get(ctx.author.id)
        if oldstate is not None:
            del self.gallery_by_msg[oldstate.msg_id]
        self.gallery_by_msg[sent.id] = state
        self.gallery_by_auth[ctx.author.id] = state

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.update_gallery(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.update_gallery(payload)

    async def update_gallery(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        gallery = self.gallery_by_msg.get(payload.message_id)
        emoji = str(payload.emoji)
        if emoji not in (self.config.left_emo, self.config.right_emo):
            return
        if gallery is None or gallery.msg_id != payload.message_id:
            return
        msg = gallery.msg
        nidx = gallery.idx
        if emoji == self.config.left_emo:
            nidx -= 1
        else:
            nidx += 1
        if nidx < 0:
            nidx = len(gallery.urls) - 1
        elif nidx >= len(gallery.urls):
            nidx = 0
        gallery.idx = nidx
        embed = discord.Embed()
        embed.set_image(url=gallery.urls[nidx][0])
        embed.set_footer(text=f"{nidx + 1}/{len(gallery.urls)}")
        await msg.edit(embed=embed)


def setup(bot):
    return bot.add_cog(Gallery(bot))
