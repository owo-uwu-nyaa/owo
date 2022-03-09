import datetime
import sys
import discord
import psycopg2
from discord.ext import commands
from psycopg2 import sql, pool
from misc import common


class Quotes(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.pool = config.pool

    @commands.group()
    async def qt(self, ctx):
        pass

    @qt.command(brief="<author> quote")
    async def add(self, ctx, member: discord.Member, *, quote: str):
        conn = self.pool.getconn()
        cur = conn.cursor()
        cur.execute(sql.SQL("insert into {} values (DEFAULT, %s, %s, %s)")
                    .format(sql.Identifier('quotes')),
                    [member.id, datetime.datetime.now(), quote])
        cur.close()
        conn.commit()
        self.pool.putconn(conn)

    @qt.command(brief="<text>")
    async def get(self, ctx, *, msg: str):
        conn = self.pool.getconn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM quotes WHERE quotes.quote ILIKE %s ESCAPE ''", (f"%%{msg.replace('%', '')}%%",))
        res = cur.fetchone()
        author_id = res[1]
        author = await common.author_id_to_obj(self.bot, author_id, ctx)
        await ctx.channel.send(f"```\n{res[3].replace('`', '')}``` - {common.get_nick_or_name(author)}")
        cur.close()
        self.pool.putconn(conn)

    @qt.command(brief="lists quotes")
    async def list(self, ctx):
        conn = self.pool.getconn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM quotes")
        res = cur.fetchall()
        for qt in res:
            author_id = qt[1]
            author = await common.author_id_to_obj(self.bot, author_id, ctx)
            await ctx.channel.send(f"```\n{qt[3].replace('`', '')}``` - {common.get_nick_or_name(author)}")
        cur.close()
        self.pool.putconn(conn)
