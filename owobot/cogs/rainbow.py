import asyncio
import colorsys
import random
import time
import discord
from discord.ext import commands, tasks

from owobot.misc import common
from owobot.misc.database import RainbowGuild


class Rainbow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await common.is_owner(ctx)

    @staticmethod
    def wrap(val):
        if val >= 1.0:
            return val - int(val)
        return val

    @staticmethod
    def gen_colors(num_colors):
        colors = []
        rand = random.random()
        for i in range(num_colors):
            rgb = colorsys.hsv_to_rgb(
                Rainbow.wrap(rand + (1.0 / num_colors) * i), 0.52, 1.0
            )
            colors.append([int(255 * x) for x in rgb])
        if random.randint(0, 1):
            colors = list(reversed(colors))
        return colors

    @commands.hybrid_group()
    async def rainbowroles(self, ctx):
        pass

    @rainbowroles.command(name="activate", brief="taste the rainbow")
    @common.long_running_command
    async def activate(self, ctx: commands.Context):
        await self._activate(ctx.guild)
        await common.react_success(ctx)
        await ctx.channel.send("Created roles, awaiting topping")

    @staticmethod
    async def _activate(guild):
        members = sorted(guild.members, key=lambda m: str(m.display_name.lower()))
        num_colors = len(members)
        colors = Rainbow.gen_colors(num_colors)
        for (member, color, i) in zip(members, colors, range(0, num_colors)):
            try:
                role = await guild.create_role(
                    name=f"rainbowify_{color}",
                    color=discord.Color.from_rgb(*color),
                    hoist=False,
                )
                await member.add_roles(role, reason="owo")
                time.sleep(0.1)
            except Exception as ex:
                print(f"{color}, aaaa, {ex}")

    @rainbowroles.command(name="deactivate", brief="delete all rainbow roles")
    @common.long_running_command
    async def deactivate(self, ctx: commands.Context):
        await self._deactivate(ctx.guild)
        await common.react_success(ctx)
        await ctx.channel.send("Until the next rainbow :>")

    @staticmethod
    async def _deactivate(guild):
        for role in guild.roles:
            if role.name.startswith("rainbowify"):
                try:
                    await role.delete()
                except Exception as ex:
                    print(f"aaa {ex}")

    @rainbowroles.command(
        name="top", brief="shuffle all rainbow roles to the second topmost position"
    )
    @common.long_running_command
    async def top(self, ctx: commands.Context):
        await self._top(ctx.guild)
        await common.react_success(ctx)
        await ctx.channel.send("Successfully did the topping, please come again!")

    @staticmethod
    async def _top(guild: discord.Guild):
        roles = {}
        highest = None
        for role in guild.me.roles:
            print(role, role.position)
            # Multiple roles can have the same position number. As a consequence of this,
            # comparing via role position is prone to subtle bugs if checking for role hierarchy.
            # The recommended and correct way to compare for roles in the hierarchy is
            # using the comparison operators on the role objects themselves. (Discord.py docs)
            if highest is None or role > highest:
                highest = role
        for role in guild.roles:
            if role.name.startswith("rainbowify"):
                roles[role] = highest.position - 1
        print(roles)
        await guild.edit_role_positions(roles)

    @tasks.loop(hours=24)
    async def schedule_refresh_rainbow(self):
        await asyncio.sleep(common.seconds_until(4, 30))
        for rgb_id in RainbowGuild.select().iterator():
            guild = self.bot.get_guild(rgb_id.snowflake)
            await self.refresh_rainbow(guild)

    async def refresh_rainbow(self, guild):
        await self._deactivate(guild)
        await self._activate(guild)
        await self._top(guild)

    @rainbowroles.command(name="refresh", brief="refresh rainbow roles")
    @common.long_running_command
    async def refresh(self, ctx: commands.Context):
        await self.refresh_rainbow(ctx.guild)


def setup(bot):
    return bot.add_cog(Rainbow(bot))
