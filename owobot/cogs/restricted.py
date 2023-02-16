import io
import logging
import time
from datetime import timedelta
from pprint import pprint
from os import path
import subprocess
import sys
import discord
from discord.ext import commands
from owobot.misc import common
from owobot.misc.database import Owner, MusicChan, db
import traceback
from typing import Optional

log = logging.getLogger(__name__)


async def _run_raw_operation(op, ctx: commands.Context):
    stdout, stderr, handler = common.redirect_string_io_std_streams()
    try:
        with handler():
            start_t = time.process_time_ns()
            value = op()
            end_t = time.process_time_ns()
        exception = None
    except Exception as e:
        exception = e
        end_t = time.process_time_ns()

    elapsed_t = timedelta(microseconds=(end_t - start_t) // 1000)
    contents = []
    if exception is not None:
        e_file = io.StringIO()
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=e_file)
        contents.append(("exception.log", e_file))
    elif value is not None:
        v_file = io.StringIO()
        pprint(value, stream=v_file)
        contents.append(("value.py", v_file))
    contents.extend((("stdout.log", stdout), ("stderr.log", stderr)))

    files = []
    for name, content in contents:
        if content.getvalue():
            content.seek(0)
            files.append(discord.File(content, filename=name))

    await ctx.send(f":stopwatch: {discord.utils.escape_markdown(str(elapsed_t))}", files=files)


class Restricted(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await common.is_owner(ctx)

    @commands.hybrid_command(aliases=["cwash"])
    async def crash(self, ctx):
        sys.exit(0)

    @commands.hybrid_command()
    async def parrot(self, ctx, *, msg: str):
        await ctx.send(msg)

    @commands.hybrid_command(aliases=["redwepoy"])
    async def redeploy(self, ctx):
        (src_path, _) = path.split(path.realpath(__file__))
        uwu = subprocess.run(
            ["git", "pull"], capture_output=True, cwd=src_path, check=False
        )
        await ctx.send(f"```\n{uwu}\n```")
        sys.exit(0)

    @commands.Cog.listener()
    async def on_ready(self):
        log.info(f"Hewoo, my name is {self.bot.user}")

    @commands.hybrid_group()
    async def owner(self, ctx):
        pass

    @owner.command(name="add", brief="add an owner")
    async def owner_add(self, ctx, member: discord.Member):
        query = Owner.insert(snowflake=member.id)
        await common.try_exe_cute_query(ctx, query)

    @owner.command(name="rm", brief="remove an owner")
    async def owner_rm(self, ctx, member: discord.Member):
        query = Owner.delete().where(Owner.snowflake == member.id)
        await common.try_exe_cute_query(ctx, query)

    @commands.hybrid_command()
    @common.long_running_command
    async def eval(self, ctx: commands.Context, code: str):
        await _run_raw_operation(lambda: eval(code, dict(), dict(context=ctx, bot=self.bot)), ctx)

    @commands.hybrid_command()
    @common.long_running_command
    async def exec(self, ctx: commands.Context, code: str):
        await _run_raw_operation(lambda: exec(code, dict(), dict(context=ctx, bot=self.bot)), ctx)

    @commands.hybrid_command()
    @common.long_running_command
    async def sql(self, ctx: commands.Context, query: str):
        await _run_raw_operation(lambda: list(db.execute_sql(query).fetchall()), ctx)

    @commands.hybrid_group()
    async def music_chan(self, ctx):
        pass

    @music_chan.command(name="add", brief="add a music_chan")
    async def music_chan_add(
        self, ctx, channel: Optional[discord.TextChannel] = commands.CurrentChannel
    ):
        query = MusicChan.insert(channel=channel.id)
        await common.try_exe_cute_query(ctx, query)

    @music_chan.command(name="rm", brief="remove a music_chan")
    async def music_chan_rm(
        self, ctx, channel: Optional[discord.TextChannel] = commands.CurrentChannel
    ):
        query = MusicChan.delete().where(MusicChan.channel == channel.id)
        await common.try_exe_cute_query(ctx, query)


def setup(bot):
    return bot.add_cog(Restricted(bot))
