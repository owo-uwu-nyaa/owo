from discord.ext import commands
import pyfiglet as fg
import cowsay

from owobot.misc import common, owolib
from owobot.misc.common import nullable_dict


def _gen_row(maxlen: int, cur_row: int):
    ltr = chr(ord("A") + cur_row)
    opad = maxlen - cur_row - 1
    if cur_row == 0:
        return f"{'.' * opad}{ltr}{'.' * opad}"
    return f"{'.' * opad}{ltr}{'.' * ((cur_row * 2) - 1)}{ltr}{'.' * opad}"


class TextUtils(commands.Cog):
    def __init__(self, bot: commands.bot.Bot):
        super().__init__()
        self.bot = bot

    @commands.hybrid_command()
    async def diamond(self, ctx, nrows: int):
        if nrows > 22:
            await ctx.send(
                f"{owolib.get_random_sorry()}, thiws is too mwuch fow me to take nyaaa~"
            )
            return
        if nrows < 1:
            await ctx.send(
                f"{owolib.get_random_sorry()}, thiws is nwot enough fow me, give me more nyaaa~"
            )
            return
        result = []
        for i in range(0, nrows - 1):
            result.append(_gen_row(nrows, i))
        for i in range(nrows - 1, -1, -1):
            result.append(_gen_row(nrows, i))
        diamond = "\n".join(result)
        await ctx.send(f"```\n{diamond}\n```")

    @commands.hybrid_command(brief="sends you your message as rendered by figlet")
    async def figlet(self, ctx: commands.Context, text: str, font: str = None, direction: str = None, justify: str = None, width: int = None):
        try:
            f = fg.Figlet(nullable_dict(font=font, direction=direction, justify=justify, width=width))
        except fg.FontNotFound:
            await common.react_failure(ctx, "font not found")
            return
        await ctx.send(f"```\n{f.renderText(text)}\n```")

    @commands.hybrid_command(brief="moo")
    async def cowsay(self, ctx: commands.Context, text: str, character: str = "cow"):
        if character not in cowsay.char_names:
            await common.react_failure(ctx, "character not found")
            return
        await ctx.send(f"```\n{cowsay.get_output_string(character, text)}\n```")


def setup(bot):
    return bot.add_cog(TextUtils(bot))
