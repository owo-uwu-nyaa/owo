import re
import threading

import discord
from discord.ext import commands
from pyspark.sql.functions import *
from pyspark.sql.types import *
from recordclass import RecordClass


class GalleryState(RecordClass):
    idx: int
    msg_id: int
    chan_id: int
    msg: discord.Message
    urls: list[str]
    embed: discord.Embed


class Gallery(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.spark_lock = threading.Lock()
        self.df_attachments = config.datalake.get_df("attachments")
        self.df_react = config.datalake.get_df("react")
        self.gallery_by_auth: dict[int, GalleryState] = dict()
        self.gallery_by_msg: dict[int, GalleryState] = dict()

    @commands.command(brief="see a gallery with all images you reacted to")
    async def gallery(self, ctx, *args):
        emotes = []
        channels = []
        for arg in args:
            if re.match(r"<a?:[^:<>@*~]+:\d+>", arg):
                emotes.append(arg)
            elif re.match(r"<#\d+>", arg):
                channels.append(int(re.search(r"\d+", arg).group(0)))
        df_reacted = self.df_react
        df_pics = self.df_attachments
        if len(emotes) > 0:
            df_reacted = df_reacted.filter(col("emoji").isin(emotes))
        if len(channels) > 0:
            df_pics = df_pics.filter(col("channel_id").isin(channels))
        df_reacted = df_reacted.filter((col("added") == True) & (col("author_id") == ctx.author.id)).select("msg_id")
        df_pics = df_pics.select("msg_id", "attachment")
        df_wanted_pics = df_reacted.join(df_pics, "msg_id").drop("msg_id").dropDuplicates().collect()
        print(df_wanted_pics)
        embed = discord.Embed()
        embed.set_image(url=df_wanted_pics[0][0])
        embed.set_footer(text=f"1/{len(df_wanted_pics)}")
        sent = await ctx.send(embed=embed)
        await sent.add_reaction(self.config.left_emo)
        await sent.add_reaction(self.config.right_emo)
        st = GalleryState(idx=0, msg_id=sent.id, chan_id=ctx.channel.id, urls=df_wanted_pics, embed=embed, msg=sent)
        oldst = self.gallery_by_auth.get(ctx.author.id)
        if oldst is not None:
            del self.gallery_by_msg[oldst.msg_id]
        self.gallery_by_msg[sent.id] = st
        self.gallery_by_auth[ctx.author.id] = st

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
        if emoji != self.config.left_emo and emoji != self.config.right_emo:
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