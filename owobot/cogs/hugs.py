import discord
from discord.ext import commands
from pygelbooru import Gelbooru
from owobot.misc import common, owolib
from owobot.misc.common import is_owner
from owobot.misc.database import NsflChan, HugShort, HugConsent


def tags_to_str(iterable):
    return "_ _\n" + "\n".join(map(lambda x: f"`{x.key} | {x.val}`", iterable))


class Hugs(commands.Cog):
    def __init__(self, bot):
        self.config = bot.config
        self.gelbooru = Gelbooru()
        self.bot = bot

    async def send_hug(self, ctx, member, img_url: str) -> None:
        query = (
            HugConsent.select()
            .where(
                (
                    (HugConsent.snowflake == member.id)
                    & (HugConsent.target == ctx.author.id)
                )
                | ((HugConsent.snowflake == member.id) & (HugConsent.target == 0))
            )
            .exists()
        )
        if ctx.author.id == member.id or query:
            hug_sender_name = (
                ctx.me.display_name
                if ctx.author.id == member.id
                else common.get_nick_or_name(ctx.author)
            )
            await ctx.send(
                f"{common.get_nick_or_name(ctx.author)} sends you a hug, {common.get_nick_or_name(member)}"
            )
            await ctx.send(img_url)
        else:
            await ctx.send(
                f"UwU, Consent is key, {common.get_nick_or_name(ctx.author)}.\n"
                f"Pwease awsk {common.get_nick_or_name(member)} for consent 🥺👉👈\n"
                f"If you want to consent, exe_cute_ `{self.bot.command_prefix}consent add {ctx.author.id}`\n"
                f"Or you can just `{self.bot.command_prefix}consent all`"
            )
        HugConsent.get_or_create(snowflake=ctx.author.id, target=member.id)

    # penguin pics
    # random.choice(["https://tenor.com/view/chibird-penguin-hug-gif-14248948", "https://tenor.com/view/cuddle-group-group-hug-friends-penguin-gif-13295520"])
    async def get_hug_gelbooru(self, ctx, tags):
        tags = tags.split(" ")
        tags.append("hug")
        blocklist = ["loli", "futanari", "shota"]
        if not NsflChan.select().where(NsflChan.channel == ctx.channel.id).exists():
            blocklist += ["rating:explicit", "nude"]
            tags.append("rating:safe")
        for i in range(0, 3):
            result = await self.gelbooru.random_post(tags=tags, exclude_tags=blocklist)
            if result is not None and result is not []:
                return result
        return "Couldn't find a hug for your request :<"

    # Nils: bonking is basically a hug
    @commands.command(brief="bonk")
    async def bonk(self, ctx, member: discord.Member):
        name = common.get_nick_or_name(ctx.author)
        other = common.get_nick_or_name(member)
        await ctx.send(
            f"{name} {owolib.owofy('bonkt')} {other} <:pingbonk:940280394736074763>"
        )

    @commands.command(brief="@someone <3 (2 boys hugging)")
    async def bhug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, "hug 2boys")
        await self.send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (customize your hug!)", aliases=["hugc"])
    async def hug(self, ctx, member: discord.Member, *tags: str):
        # convert tags to a space separated string, as thats what get_hug_gelbooru expects
        gelbooru_url = await self.get_hug_gelbooru(ctx, " ".join(tags))
        await self.send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (people hugging)")
    async def ahug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, "hug androgynous")
        await self.send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="@someone <3 (2 girls hugging)")
    async def ghug(self, ctx, member: discord.Member):
        gelbooru_url = await self.get_hug_gelbooru(ctx, "hug 2girls")
        await self.send_hug(ctx, member, str(gelbooru_url))

    @commands.command(brief="Use the tag shorthands uwu :)")
    async def h(self, ctx, member: discord.Member, *short: str):
        tags = ""
        if len(short) > 0:
            query = HugShort.select().where(HugShort.key.in_(list(short[0])))
            tags = (
                " ".join(map(lambda x: str(x.val), list(query)))
                + " "
                + " ".join(short[1:])
            )
        gelbooru_url = await self.get_hug_gelbooru(ctx, tags)
        await self.send_hug(ctx, member, str(gelbooru_url))

    @commands.group()
    async def hugconfigure(self, ctx):
        pass

    @hugconfigure.command(
        name="explain", brief="explain what a short str is translated to"
    )
    async def hugconfigure_explain(self, ctx, short: str):
        query = HugShort.select().where(HugShort.key.in_(list(short)))
        await ctx.channel.send(tags_to_str(query))

    @hugconfigure.command(name="list", brief="list tag short")
    async def hugconfigure_list(self, ctx):
        query = HugShort.select()
        await ctx.channel.send(tags_to_str(query))

    @commands.check(is_owner)
    @hugconfigure.command(name="add", brief="add a tag short")
    async def hugconfigure_add(self, ctx, short: str, tag: str):
        if len(short) != 1:
            await common.react_failure(ctx)
            return
        query = HugShort.insert(key=short, val=tag)
        await common.try_exe_cute_query(ctx, query)

    @commands.check(is_owner)
    @hugconfigure.command(name="rm", brief="rm a tag short")
    async def hugconfigure_rm(self, ctx, short: str):
        query = HugShort.delete().where(HugShort.key == short)
        await common.try_exe_cute_query(ctx, query)

    @commands.group(pass_context=True)
    async def consent(self, ctx):
        pass

    @consent.command(name="add", brief="consent to hugs by id")
    async def consent_add(self, ctx, member: discord.Member):
        if ctx.author.id == member.id:
            await ctx.channel.send("You can always hug yourself :>")
            return
        query = HugConsent.insert(snowflake=ctx.author.id, target=member.id)
        await common.try_exe_cute_query(ctx, query)

    @consent.command(name="all", brief="blanket consent to hugs")
    async def consent_all(self, ctx):
        query = HugConsent.insert(snowflake=ctx.author.id, target=0)
        await common.try_exe_cute_query(ctx, query)

    @consent.command(name="undoall", brief="un-blanket consent to hugs")
    async def consent_undoall(self, ctx):
        query = HugConsent.delete().where(
            (HugConsent.snowflake == ctx.author.id) & (HugConsent.target == 0)
        )
        await common.try_exe_cute_query(ctx, query)

    @consent.command(name="rm", brief="unconsent to hugs by id")
    async def consent_rm(self, ctx, member: discord.Member):
        query = (
            HugConsent.delete()
            .where(
                (HugConsent.snowflake == ctx.author.id)
                & (HugConsent.target == member.id)
            )
            .execute()
        )
        await common.try_exe_cute_query(ctx, query)

    @consent.command(name="rmrf", brief="unconsent to all hugs")
    async def consent_rmrf(self, ctx):
        query = HugConsent.delete().where(HugConsent.snowflake == ctx.author.id)
        await common.try_exe_cute_query(ctx, query)


def setup(bot):
    bot.add_cog(Hugs(bot))
