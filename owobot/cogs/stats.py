import asyncio
import os

os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.kudu:kudu-spark3_2.12:1.15.0 pyspark-shell'
import io
import threading
import discord
import plotly.express as px
from discord.ext import commands
from pyspark.shell import spark
import pyspark.sql.functions as F
from pyspark.sql.types import LongType
from misc import common


def get_show_string(df, n=20, truncate=True, vertical=False):
    if isinstance(truncate, bool) and truncate:
        return df._jdf.showString(n, 20, vertical)
    return df._jdf.showString(n, int(truncate), vertical)


def count_words(df) -> str:
    dfw = df.select(F.explode(
        F.split(F.regexp_replace(F.regexp_replace(F.lower(F.col("msg")), "[^a-z $]", ""), " +", " "), " ")).alias(
        "word")) \
        .groupBy("word") \
        .count() \
        .orderBy("count", ascending=False)
    return get_show_string(dfw, n=20)


class Stats(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.spark_lock = threading.Lock()
        self.df_global = config.datalake.get_df("msgs")

    async def cog_check(self, ctx):
        if not self.spark_lock.locked():
            return True
        await ctx.channel.send("Sorry, another query seems to be running")
        return False

    def get_messages_by_author(self, ctx):
        return self.df_global.filter((F.col("author_id") == ctx.author.id) & (F.col("guild_id") == ctx.guild.id))

    def get_guild_df(self, ctx):
        return self.df_global.filter(F.col("guild_id") == ctx.guild.id)

    async def get_id_name_df(self, ctx):
        mmap = []
        for member in ctx.guild.members:
            mmap.append((common.get_nick_or_name(member), member.id))

        return spark.createDataFrame(data=mmap, schema=["name", "id"])

    @commands.group()
    async def stats(self, ctx):
        pass

    @stats.command(brief="when do you procrastinate?")
    async def activity(self, ctx):
        with self.spark_lock:
            dfa = self.get_messages_by_author(ctx).select("time")
            dft = dfa.groupBy(F.hour("time").alias("hour")).agg(F.count("time").alias("count"))
            dft = dft.orderBy("hour")
            res = get_show_string(dft, n=24)
            await ctx.channel.send(f'```\n{res}total messages: {dfa.count()}```')

    @stats.command(brief="use your words")
    async def words(self, ctx):
        with self.spark_lock:
            dfa = self.get_messages_by_author(ctx)
            res = count_words(dfa)
            await ctx.channel.send(f'```\n{common.sanitize_markdown(res)}\n```')

    @stats.command(brief="words, but also use messages from dms/other guilds")
    async def simonwords(self, ctx):
        with self.spark_lock:
            dfa = self.df_global.filter(F.col("author_id") == ctx.author.id)
            res = count_words(dfa)
            await ctx.channel.send(f'```\n{common.sanitize_markdown(res)}\n```')

    @stats.command(brief="words, but emotes", aliases=["emo"])
    async def emotes(self, ctx):
        with self.spark_lock:
            dfa = self.get_messages_by_author(ctx)
            dfw = dfa.select(F.explode(F.expr("regexp_extract_all(msg, '<a?:[^:<>@*~]+:\\\\d+>', 0)")).alias("emote")) \
                .groupBy("emote") \
                .count() \
                .orderBy("count", ascending=False) \
                .limit(20)
            pandas_df = dfw.toPandas().sort_values(by=["count"])
            maxlen = len(str(pandas_df["count"].max()))
            uwu = ["_ _"]
            for row in pandas_df.itertuples():
                uwu.append(f"`{str(row[0]).rjust(maxlen, ' ')}` | {row[1]}")
            await ctx.channel.send("\n".join(uwu))

    @stats.command(brief="use your ~~words~~ letters")
    async def letters(self, ctx):
        with self.spark_lock:
            dfa = self.get_messages_by_author(ctx)
            dfl = dfa.select(F.explode(F.split(F.col("msg"), "")).alias("letter")) \
                .groupBy("letter") \
                .count() \
                .filter(F.ascii("letter") != 0) \
                .orderBy("count", ascending=False)
            res = get_show_string(dfl, n=20)
            await ctx.channel.send(f'```\n{res.replace("`", "")}\n```')

    @stats.command(brief="make history", aliases=["histowowy"])
    async def history(self, ctx, *members: discord.Member):
        with self.spark_lock:
            # gather relevant authors
            author_mappings = []
            if len(members) == 0:
                dfq = self.get_guild_df(ctx).groupBy("author_id").count().orderBy("count", ascending=False).limit(10)
                for row in dfq.collect():
                    try:
                        name = (await common.author_id_to_obj(self.bot, row["author_id"], ctx)).display_name
                        author_mappings.append((name, row["author_id"]))
                    except:
                        author_mappings.append((str(row["author_id"]), row["author_id"]))
            else:
                for member in members:
                    author_mappings.append((common.get_nick_or_name(member), member.id))
            author_mappings_df = spark.createDataFrame(data=author_mappings, schema=["name", "id"])
            # get msg counts
            dfg = self.get_guild_df(ctx).select("author_id", "time")
            dft = dfg.join(author_mappings_df.drop("name"), dfg["author_id"] == author_mappings_df["id"]) \
                .withColumn("date", F.date_trunc("day", "time")) \
                .groupBy("date", "author_id") \
                .agg(F.count("date").alias("count"))
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
        with self.spark_lock:
            n_limit = 30
            df_hugs = self.get_guild_df(ctx).select("author_id", "msg") \
                .withColumn("hug_target",
                            F.regexp_extract(
                                F.col("msg"),
                                r"(?<=(^\$(hug|hugc|ahug|bhug|ghug|dhug|h).{0,10})<@!?)\\d{17,19}(?=(>*.))",
                                0)
                            .cast(LongType())) \
                .drop("msg")
            df_hug_counts = df_hugs.filter(df_hugs["hug_target"].isNotNull()) \
                .rdd.map(lambda x: (x[0], x[1]) if x[0] > x[1] else (x[1], x[0])) \
                .toDF() \
                .groupBy(["_1", "_2"]) \
                .count() \
                .orderBy("count", ascending=False) \
                .limit(n_limit)
            author_mappings = await self.get_id_name_df(ctx)
            df_hug_counts_names = df_hug_counts.join(author_mappings, df_hug_counts["_1"] == author_mappings["id"]) \
                .withColumnRenamed("name", "#1").drop("id", "_1") \
                .join(author_mappings, df_hug_counts["_2"] == author_mappings["id"]) \
                .withColumnRenamed("name", "#2").drop("id", "_2") \
                .orderBy("count", ascending=False) \
                .select("#1", "#2", "count")
            res = get_show_string(df_hug_counts_names, n_limit)
            await ctx.channel.send(f'```\n{res.replace("`", "")}\n```')
