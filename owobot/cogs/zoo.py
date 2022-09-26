import re

import discord
import peewee
from discord.ext import commands
from recordclass import RecordClass
from typing import Optional

from owobot.misc import common
from owobot.owobot import OwOBot
from owobot.misc.database import (
    BaaPics,
    BaaUsers,
    AwooPics,
    AwooUsers,
    RawwrPics,
    RawwrUsers,
    MooUsers,
    MooPics,
    NyaaPics,
    NyaaUsers,
    PikaUsers,
    PikaPics,
)


class Animal(RecordClass):
    sound: str
    sound_regex: re.Pattern
    pics: peewee.Model
    users: peewee.Model


def _create_animal(sound, sound_pattern, pics, users):
    return Animal(sound, re.compile(sound_pattern), pics, users)


_animals = {
    "baa": _create_animal("baa", "baa+", BaaPics, BaaUsers),
    "awoo": _create_animal("awoo", "awoo+", AwooPics, AwooUsers),
    "rawr": _create_animal("rawwr", "raw+r", RawwrPics, RawwrUsers),
    "nyaa": _create_animal("nyaa", "nya+", NyaaPics, NyaaUsers),
    "moo": _create_animal("moo", "moo+", MooPics, MooUsers),
    "pika": _create_animal("pika", "pika+", PikaPics, PikaUsers),
}


def _get_animal_by_sound(sound: str) -> Optional[Animal]:
    for animal in _animals.values():
        if animal.sound_regex.match(sound):
            return animal


class _ZooConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, sound: str) -> Animal:
        animal = _get_animal_by_sound(sound)
        if animal is not None:
            return animal
        else:
            await common.react_failure(
                ctx, f"old macdonald didn't have that animal on his farm :("
            )
            raise commands.BadArgument(sound)


_AnimalT = common.Annotated[Animal, _ZooConverter]


class Zoo(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await common.is_owner(ctx)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        sound = common.remove_prefix(
            prefix=self.bot.command_prefix, content=message.content
        )
        if sound is None:
            return

        animal = _get_animal_by_sound(sound)
        if animal is not None:
            self.bot.handle_dynamic(message)
            pingpong = animal.users.select().order_by(peewee.fn.Random()).get()
            pic = animal.pics.select().order_by(peewee.fn.Random()).get().picture
            await message.channel.send(f"<@{pingpong.snowflake}>")
            await message.channel.send(pic)

    @commands.hybrid_group()
    async def zoo(self, ctx):
        pass

    @zoo.group()
    async def user(self, ctx):
        pass

    @user.command(name="add", brief="add user to animal list")
    async def user_add(self, ctx, animal: _AnimalT, member: discord.Member):
        query = animal.users.insert(snowflake=member.id)
        await common.try_exe_cute_query(ctx, query)
        await common.react_success(ctx, f"added {member} to {animal.sound} list")

    @user.command(name="rm", brief="rm user from animal list")
    async def user_rm(self, ctx, animal: _AnimalT, member: discord.Member):
        query = animal.users.delete().where(animal.users.snowflake == member.id)
        await common.try_exe_cute_query(ctx, query)

    @zoo.group()
    async def pic(self, ctx):
        pass

    @pic.command(name="add", brief="add pic to animal list")
    async def pic_add(self, ctx, animal: _AnimalT, pic: str):
        query = animal.pics.insert(picture=pic)
        await common.try_exe_cute_query(ctx, query)

    @pic.command(name="rm", brief="rm pic from animal list")
    async def pic_rm(self, ctx, animal: _AnimalT, pic: str):
        query = animal.pics.delete().where(animal.pics.picture == pic)
        await common.try_exe_cute_query(ctx, query)


def setup(bot):
    return bot.add_cog(Zoo(bot))
