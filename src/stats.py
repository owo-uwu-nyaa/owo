import threading
import io
import discord
import pandas

import common
import plotly.express as px

from discord.ext import commands
from pyspark.shell import spark
from pyspark.sql.functions import *
from pyspark.sql.types import *


def get_show_string(df, n=20, truncate=True, vertical=False):
    if isinstance(truncate, bool) and truncate:
        return df._jdf.showString(n, 20, vertical)
    else:
        return df._jdf.showString(n, int(truncate), vertical)


class Stats(commands.Cog):
    def __init__(self, bot, bpath):
        self.bot = bot
        self.spark_lock = threading.Lock()

        schema = StructType([
            StructField("author_id", LongType(), False),
            StructField("channel_id", LongType(), False),
            StructField("time", DoubleType(), False),
            StructField("msg", StringType(), False)
        ])

        self.df = spark.read \
            .option("header", True) \
            .option("multiLine", True) \
            .option("escape", '"') \
            .schema(schema) \
            .csv(bpath + "msgs.csv")

        self.df = self.df.withColumn("u_time", from_unixtime("time")).drop("time")

    def get_messages_by_author(self, author):
        rejectChans = [937308889425281034, 946545522167124000, 779413828051664966]
        return self.df.filter((col("author_id") == author.id) & (~self.df["channel_id"].isin(rejectChans)))

    async def check_allow_query(self, ctx):
        if self.spark_lock.locked():
            await ctx.channel.send(f"Sorry, another query seems to be running")
            return False
        return True

    @commands.group()
    async def stats(self, ctx):
        pass

    @stats.command(brief="when do you procrastinate?")
    async def activity(self, ctx):
        if not await self.check_allow_query(ctx):
            return
        with self.spark_lock:
            dfa = self.get_messages_by_author(ctx.author)
            dft = dfa.groupBy(hour("u_time").alias("hour")).agg(count("u_time").alias("count"))
            dft = dft.orderBy("hour")
            res = get_show_string(dft, n=24)
            await ctx.channel.send(f'```\n{res}total messages: {dfa.count()}```')

    @stats.command(brief="use your words")
    async def words(self, ctx):
        if not await self.check_allow_query(ctx):
            return
        with self.spark_lock:
            dfa = self.get_messages_by_author(ctx.author)
            dfw = dfa.withColumn("word", explode(split(col("msg"), " "))) \
                .groupBy("word") \
                .count() \
                .orderBy("count", ascending=False)
            res = get_show_string(dfw, n=20)
            await ctx.channel.send(f'```\n{res.replace("`", "")}\n```')

    @stats.command(brief="use your ~~words~~ letters")
    async def letters(self, ctx):
        if not await self.check_allow_query(ctx):
            return
        with self.spark_lock:
            dfa = self.get_messages_by_author(ctx.author)
            dfl = dfa.withColumn("letter", explode(split(col("msg"), ""))) \
                .groupBy("letter") \
                .count() \
                .filter(ascii("letter") != 0) \
                .orderBy("count", ascending=False)
            res = get_show_string(dfl, n=20)
            await ctx.channel.send(f'```\n{res.replace("`", "")}\n```')

    @stats.command(brief="make history")
    async def history(self, ctx, *members: discord.Member):
        if not await self.check_allow_query(ctx):
            return
        with self.spark_lock:
            author_mappings = []
            if len(members) == 0:
                dfq = self.df.groupBy("author_id").count().orderBy("count", ascending=False).limit(10)
                for r in dfq.collect():
                    author_mappings.append((common.get_nick_or_name(
                        await common.author_id_to_obj(self.bot, r["author_id"], ctx)), r["author_id"]))
            else:
                for m in members:
                    author_mappings.append((common.get_nick_or_name(m), m.id))
            author_mappings_df = spark.createDataFrame(data=author_mappings, schema=["name", "id"])
            dft = self.df.drop("channel_id", "msg") \
                .join(author_mappings_df.drop("name"), self.df["author_id"] == author_mappings_df["id"]) \
                .withColumn("date", date_trunc("day", "u_time")) \
                .groupBy("date", "author_id") \
                .agg(count("date").alias("count"))
            dfp = dft.toPandas() \
                .pivot(index="date", columns="author_id", values="count") \
                .asfreq("1D", fill_value=0) \
                .fillna(0) \
                .reset_index() \
                .melt(id_vars=["date"]) \
                .join(author_mappings_df.toPandas().set_index("id"), on="author_id")
            fig = px.line(dfp, x="date", y="value", color="name")
            img = io.BytesIO()
            fig.write_image(img, format="png", scale=3)
            img.seek(0)
            await ctx.channel.send(file=discord.File(fp=img, filename="yeet.png"))