import asyncio
import io
import threading
import discord
import plotly.express as px
from discord.ext import commands
from pyspark.shell import spark
from pyspark.sql.functions import *
from pyspark.sql.types import *

from owobot.misc import common


def get_show_string(df, n=20, truncate=True, vertical=False):
    if isinstance(truncate, bool) and truncate:
        return df._jdf.showString(n, 20, vertical)
    else:
        return df._jdf.showString(n, int(truncate), vertical)


class Stats(commands.Cog):
    def __init__(self, bot, message_file):
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
            .csv(message_file)

        # TODO fix this by writing and using guild ids
        # unfortunately, i did not write the guild id with old messages - these are dumb hardcoded channels which contain garbage messages
        rejectChans = [937308889425281034, 946545522167124000, 779413828051664966, 498443061316157455,
                       170911988346519553, 877658158460452874, 779414116812849192, 194411030607167491]
        self.df = self.df.filter(~self.df["channel_id"].isin(rejectChans)) \
            .withColumn("u_time", from_unixtime("time")).drop("time")

    def get_messages_by_author(self, author):
        return self.df.filter((col("author_id") == author.id))

    async def check_allow_query(self, ctx):
        if self.spark_lock.locked():
            await ctx.channel.send(f"Sorry, another query seems to be running")
            return False
        return True

    async def get_names_from_df(self, ctx, relevant_hug_ids):
        # TODO this cant be really the correct way of gathering all names, is this even done in parallel? Maybe pycord blocks?
        async def f(r):
            return (
                common.get_nick_or_name(await common.author_id_to_obj(self.bot, r["author_id"], ctx)), r["author_id"])

        mappings = await asyncio.gather(*[f(r) for r in relevant_hug_ids.collect()])
        return spark.createDataFrame(data=mappings, schema=["name", "id"])

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

    @stats.command(brief="make history", aliases=["histowowy"])
    async def history(self, ctx, *members: discord.Member):
        if not await self.check_allow_query(ctx):
            return
        with self.spark_lock:
            # gather relevant authors
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
            # get msg counts
            dft = self.df.drop("channel_id", "msg") \
                .join(author_mappings_df.drop("name"), self.df["author_id"] == author_mappings_df["id"]) \
                .withColumn("date", date_trunc("day", "u_time")) \
                .groupBy("date", "author_id") \
                .agg(count("date").alias("count"))
            # fill gaps in data with zeros, replace ids with names
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
            await ctx.channel.send(file=discord.File(fp=img, filename="../yeet.png"))

    @stats.command(brief="see all the lovebirbs #choo choo #ship", aliases=["ships"])
    async def couples(self, ctx):
        if not await self.check_allow_query(ctx):
            return
        with self.spark_lock:
            n_limit = 30
            df_hugs = self.df.drop("channel_id", "u_time") \
                .withColumn("hug_target",
                            regexp_extract(
                                col("msg"), "(?<=(^\$(hug|hugc|ahug|bhug|ghug|dhug).{0,10})<@!?)\\d{17,19}(?=(>*.))", 0)
                            .cast(LongType())) \
                .drop("msg")
            df_hug_counts = df_hugs.filter(df_hugs["hug_target"].isNotNull()) \
                .rdd.map(lambda x: (x[0], x[1]) if x[0] > x[1] else (x[1], x[0])) \
                .toDF() \
                .groupBy(["_1", "_2"]) \
                .count() \
                .orderBy("count", ascending=False) \
                .limit(n_limit)
            relevant_hug_ids = df_hug_counts.select("_1").withColumnRenamed("_1", "author_id") \
                .union(df_hug_counts.select("_2").withColumnRenamed("_2", "author_id")) \
                .drop_duplicates()
            author_mappings = await self.get_names_from_df(ctx, relevant_hug_ids)
            df_hug_counts_names = df_hug_counts.join(author_mappings, df_hug_counts["_1"] == author_mappings["id"]) \
                .withColumnRenamed("name", "#1").drop("id", "_1") \
                .join(author_mappings, df_hug_counts["_2"] == author_mappings["id"]) \
                .withColumnRenamed("name", "#2").drop("id", "_2") \
                .orderBy("count", ascending=False) \
                .select("#1", "#2", "count")
            res = get_show_string(df_hug_counts_names, n_limit)
            await ctx.channel.send(f'```\n{res.replace("`", "")}\n```')
