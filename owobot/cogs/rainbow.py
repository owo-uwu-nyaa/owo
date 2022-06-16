import colorsys
import random
import time

import discord
from discord.ext import commands

from owobot.misc import common


class Rainbow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await common.is_owner(ctx)

    @staticmethod
    def wrap(val):
        if val >= 1.:
            return val - int(val)
        return val

    @staticmethod
    def gen_colors(num_colors):
        colors = []
        rand = random.random()
        for i in range(num_colors):
            rgb = colorsys.hsv_to_rgb(Rainbow.wrap(rand + (1.0 / num_colors) * i), 0.52, 1.0)
            colors.append([int(255 * x) for x in rgb])
        return colors

    @commands.group()
    async def rainbowroles(self, ctx):
        pass

    @rainbowroles.command(name="activate", brief="taste the rainbow")
    async def activate(self, ctx):
        members = sorted(ctx.guild.members, key=lambda m: m.display_name.lower())
        num_colors = len(members)
        colors = self.gen_colors(num_colors)
        for (member, color, i) in zip(members, colors, range(0, num_colors)):
            try:
                role = await ctx.guild.create_role(
                    name=f"rainbowify_{color}",
                    color=discord.Color.from_rgb(*color),
                    hoist=False
                )
                await member.add_roles(role, reason="owo")
                time.sleep(0.1)
            except Exception as ex:
                print(color)
        await common.react_success(ctx)
        await ctx.channel.send("Created roles, awaiting topping")

    @rainbowroles.command(name="deactivate", brief="delete all rainbow roles")
    async def deactivate(self, ctx):
        for role in ctx.guild.roles:
            if role.name.startswith("rainbowify"):
                try:
                    await role.delete()
                except Exception as ex:
                    print("aaa")
        await common.react_success(ctx)
        await ctx.channel.send("Until the next rainbow :>")

    @rainbowroles.command(name="top", brief="shuffle all rainbow roles to the second topmost position")
    async def top(self, ctx):
        num_roles = len(ctx.guild.roles)
        roles = {}
        for role in ctx.guild.roles:
            if role.name.startswith("rainbowify"):
                roles[role] = num_roles - 2
        print(roles)
        await ctx.guild.edit_role_positions(roles)
        await common.react_success(ctx)
        await ctx.channel.send("Successfully did the topping, please come again!")

def setup(bot):
    bot.add_cog(Rainbow(bot))
