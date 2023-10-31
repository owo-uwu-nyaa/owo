import asyncio
import colorsys
import random
import time
import discord
from discord.ext import commands, tasks

from owobot.misc import common
from owobot.misc.database import RainbowGuild

def get_rgb_color(i, n):
    return [int(255*x) for x in colorsys.hsv_to_rgb(Rainbow.wrap(0.15 + (1.0 / n) * i), 0.82, 0.98)]


async def role_members(ctx, x) -> int:
    c = 0
    for i, member, role in x:
        if i >= len(x*2):
            print(i, member, role)
            await ctx.send("not enough roles grrr!")
            break
        ok = await role_user(member,role)
        if ok: c+=1
    return c

async def role_user(member, role) -> bool:
    for r in member.roles:
        if r == role:
            continue
        if "rainbowify" in r.name:
            try:
                await member.remove_roles(r, reason="rainbow")
            except Exception as e:
                print(member, role)
                print("Error while removing role", e)
    if not role in member.roles:
        try:
            await member.add_roles(role, reason="rainbow")
            return True
        except Exception as e:
            print(member,role)
            print("Error while adding role", e)
    return False
            
class Rainbow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await common.is_owner(ctx) 
    
    @commands.hybrid_command()
    @common.long_running_command
    async def rainbowshuffle(self, ctx):
        '''
        Similar to `rainbowroles activate`, but with a much lower execution time and less ratelimits 
        (especially for an already rainbowified guild).

        Instead of creating new roles, we reorder the existing roles and then match them with a member.
        This means, if only one member needs new roles or has changed their nickname, we don't need to
        recreate every role, we simply "shuffle" the roles up/down.

        Under the hood this uses `get_rgb_color` to procedurally generate a color for a given index.
        This means, if we don't have enough roles, we simply create them at the end of the existing roles! 
        
        Lastly, we can divide and conquer by splitting the member list into two, giving each to an asyncio task.
        '''
        await ctx.send(":rainbow: rainbowifying guild!!")
        t0 = time.perf_counter()

        roles = list(filter(lambda role: role.name.startswith("rainbowify"), ctx.guild.roles))
        members = sorted(ctx.guild.members, key=lambda m: m.display_name.lower())
        
        n_members = len(members)
        n_roles = len(roles)

        created_roles = 0

        d = n_roles - n_members
        if d < 0:
            await ctx.send(f"We need to create more roles! Members: {n_members} Roles: {n_roles}\n:warning: Warning, this might take a while!")
            for i in range(0,-d):
                if i % 5 == 0: time.sleep(0.5)
                rgb = get_rgb_color(n_roles+i, n_members)
                role = await ctx.guild.create_role(
                    name=f"rainbowify_{n_roles+i}_{rgb}",
                    color=discord.Color.from_rgb(*rgb),
                    hoist=False,
                )
                roles.append(role)
                created_roles += 1
        elif d > 0:
            await ctx.send(f"There are more roles than necessary. You might want to consider removing some. Members: {n_members} Roles: {n_roles}")

        roles = sorted(roles, key=lambda t: int(t.name.split("_")[1]),reverse=random.randint(0,1))

        if created_roles > 0: await ctx.send(f"Added {created_roles} new rainbow roles!")
        await ctx.send("Done preprocessing. I will now assign the roles!")

        n = len(roles) // 2    
        x = list(zip(range(0,len(roles)),members,roles,))

        tasks = [
            asyncio.create_task(role_members(ctx, x[:n])),
            asyncio.create_task(role_members(ctx, x[n:])),
        ]
        
        # Wait for all tasks to complete and retrieve their results
        results = await asyncio.gather(*tasks)

            
        # for id, rgb, role in roles:
        #     print(id, rgb, role)
        # print(roles)
        await ctx.send(f"rainbowification complete! ive roled {sum(results)} users. This took {time.perf_counter() - t0:.3f} seconds.")


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
                Rainbow.wrap(0.15 + (1.0 / num_colors) * i), 0.82, 0.98
           )
            #m = i % 2
            #if m  == 0:
            #3    rgb = (195, 15, 22)
            #elif m == 1:
            #    rgb = (7, 159, 65)
            #colors.append(rgb)
            colors.append([int(255 * x) for x in rgb])
        if random.randint(0, 1):
            colors = colors[0:1] + list(reversed(colors[1:]))
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
        hidx = 0
        members = members[hidx:] + members[:hidx]

        num_colors = len(members)
        colors = Rainbow.gen_colors(num_colors)
        for (member, color, i) in zip(members, colors, range(0, num_colors)):
            try:
                role = await guild.create_role(
                    name=f"rainbowify_{i}_{color}",
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
        #await self._top(guild)

    @rainbowroles.command(name="refresh", brief="refresh rainbow roles")
    @common.long_running_command
    async def refresh(self, ctx: commands.Context):
        await self.refresh_rainbow(ctx.guild)


def setup(bot):
    return bot.add_cog(Rainbow(bot))
