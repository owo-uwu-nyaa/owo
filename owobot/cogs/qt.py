from discord.ext import commands
from owobot.misc import common


class Qt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await common.is_owner(ctx)

    @commands.hybrid_group()
    async def qt(self, ctx):
        pass

    @qt.command(name="activate", brief="prepare for qt")
    async def qt_activate(self, ctx: commands.Context):
        async with ctx.typing():
            for member in ctx.guild.members:
                try:
                    role = await ctx.guild.create_role(
                        name=f"qt_{member.display_name}",
                        hoist=False
                    )
                    await member.add_roles(role, reason="owo")
                    await member.edit(nick="qt")
                except Exception as ex:
                    print(f"{member} did aaaaa {ex}")
            await common.react_success(ctx)
            await ctx.channel.send("uwu")

    @qt.command(name="deactivate", brief="revert names")
    async def qt_deactivate(self, ctx: commands.Context):
        async with ctx.typing():
            for member in ctx.guild.members:
                for role in member.roles:
                    rn = role.name
                    if rn.startswith("qt_"):
                        try:
                            await member.edit(nick=rn[3:])
                        except Exception as ex:
                            print(f"aaa {ex}")
            await common.react_success(ctx)
            await ctx.channel.send("reverted names")

    @qt.command(name="yeet", brief="delete nameroles")
    async def qt_yeet(self, ctx: commands.Context):
        async with ctx.typing():
            for member in ctx.guild.members:
                for role in member.roles:
                    rn = role.name
                    if rn.startswith("qt_"):
                        try:
                            await member.edit(nick=rn[3:])
                            await role.delete()
                        except Exception as ex:
                            print("aaa")
            await common.react_success(ctx)
            await ctx.channel.send("reverted and yeeted roles")


def setup(bot):
    return bot.add_cog(Qt(bot))
