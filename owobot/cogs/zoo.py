import random
import re
from copy import deepcopy
from typing import TypeVar

import discord
import peewee
from discord.ext import commands
from recordclass import RecordClass

from owobot.misc import database, common
from owobot.misc.database import BaaPics, BaaUsers, AwooPics, AwooUsers, RawwrPics, RawwrUsers, MooUsers, MooPics, \
    NyaaPics, NyaaUsers


class Animal(RecordClass):
    sound: str
    sound_regex: str
    pics: peewee.Model
    users: peewee.Model

#TODO somehow dynmaically create tables, maybe ditch ORM?
class Zoo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.animals = {"baa": Animal("baa", "baa+", BaaPics, BaaUsers),
                        "awoo": Animal("awoo", "awoo+", AwooPics, AwooUsers),
                        "rawr": Animal("rawwr", "raw+r", RawwrPics, RawwrUsers),
                        "nyaa": Animal("nyaa", "nya+", NyaaPics, NyaaUsers),
                        "moo": Animal("moo", "moo+", MooPics, MooUsers)}

    async def cog_check(self, ctx):
        return await common.is_owner(ctx)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        for animal in self.animals.values():
            if re.match(fr"^[{self.bot.command_prefix}]{animal.sound_regex}$", message.content):
                pingpong = animal.users.select().order_by(peewee.fn.Random()).get()
                pic = animal.pics.select().order_by(peewee.fn.Random()).get().picture
                await message.channel.send(f"<@{pingpong.snowflake}>")
                await message.channel.send(pic)

    @commands.group()
    async def zoo(self, ctx):
        pass

    @zoo.group()
    async def user(self, ctx):
        pass

    @user.command(name="add", brief="add user to animal list")
    async def user_add(self, ctx, table: str, member: discord.Member):
        query = self.animals[table].users.insert(snowflake=member.id)
        await common.try_exe_cute_query(ctx, query)

    @user.command(name="rm", brief="rm user from animal list")
    async def user_rm(self, ctx, table: str, member: discord.Member):
        query = self.animals[table].users.delete().where(self.user_table.snowflake == member.id)
        await common.try_exe_cute_query(ctx, query)

    @zoo.group()
    async def pic(self, ctx):
        pass

    @pic.command(name="add", brief="add pic to animal list")
    async def pic_add(self, ctx, table: str, pic: str):
        query = self.animals[table].pics.insert(picture=pic)
        await common.try_exe_cute_query(ctx, query)

    @pic.command(name="rm", brief="rm pic from animal list")
    async def pic_rm(self, ctx, table: str, pic: str):
        query = self.animals[table].pics.delete().where(self.pic_table.picture == pic)
        await common.try_exe_cute_query(ctx, query)


def setup(bot):
    bot.add_cog(Zoo(bot))
