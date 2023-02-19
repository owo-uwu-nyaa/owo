import datetime
import io
import logging

import discord
import pandas as pd
import plotly.express as px
from discord.ext import tasks, commands

import math
from owobot.owobot import OwOBot
from owobot.misc import mensa_api

log = logging.getLogger(__name__)

def mensa_embed_builder(mensa, date):
    '''
    Returns a discord.Embed object initialized with Mensa name and date
    '''
    embed = discord.Embed(
        title=f'{date.strftime("%A, %-d %b %Y")}',
        color=0x3edb53
    )

    embed.timestamp = date
    embed.set_author(name="Mensa " + mensa["display_name"])
    return embed

def get_next_open_date(date):
    '''
    Returns the next trivial open date (does not account for holidays)
    - If past 3pm on a weekday, return the next day
    - If on a weekend, return the next monday
    - Otherwise return the original date
    '''
    weekday = date.weekday()
    if weekday > 4:
        date += datetime.timedelta(days=7-weekday)
    elif date.hour > 15:
        date += datetime.timedelta(days=1)
    return date

class Mensa(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot
        self.update_channel.start()

        
    async def info(self, ctx, mensa_name="garching"):
        '''
        Sends information as embed about the requested canteen, if no target is provided, default to Garching.
        Contains:
            - Current mensa occupation
            - Menu summary for the next open day
        '''
        mensa = await mensa_api.mensa_from_string(mensa_name)
        if not mensa:
            return await ctx.send("Please select one of the following canteens: " + ", ".join(mensa_api.MENSA_LIST.keys()))

        date = get_next_open_date(datetime.datetime.today())

        occupation = await mensa_api.get_occupancy(mensa)
        capacity = mensa.get("capacity")
        percent = min(occupation / capacity if capacity else 0, 1)
        
        bar = "🟦 " * math.ceil(percent*10) + "⬜ " * math.floor((1-percent)*10)

        dishes_today = await mensa_api.get_dishes_for_date(mensa, date)

        embed = mensa_embed_builder(mensa, date)
        embed.set_image(url=mensa["thumbnail"])
        embed.description = "[ " + str(int(occupation)) + f" :people_hugging: ] " + ((bar + f"({round(percent*100,2):1.2f}%)") if capacity else "")    

        labels = {}
        for dish in dishes_today:
            dish_type = dish.get("dish_type")
            if not labels.get(dish_type):
                labels[dish_type] = []
            labels[dish_type].append(dish)
        
        for dish_type, label in labels.items():
            if dish_type != "Beilagen":

                value = "\n".join(list(map(lambda x : "- " + x.get("name", ""), label)))
                embed.add_field(name= dish_type + " " + mensa_api.TYPES.get(dish_type, "") , value=value, inline=True)     
                continue
            embed.add_field(name="More", value=f'Other {len(label)} side-dishes can be seen with the command `{self.bot.command_prefix}mensa menu`' , inline=True)     

        await ctx.send(embed=embed)

    async def menu(self, ctx, mensa_name="garching", page_number=1, page_size=6):
        '''
        Sends an embed containing paginated menu dishes for the next available day
        Pages can be iterated by changing page number, which simply splices the original dishes array
        '''
        mensa = await mensa_api.mensa_from_string(mensa_name)
        if not mensa:
            return await ctx.send("Please select one of the following canteens: " + ", ".join(mensa_api.MENSA_LIST.keys()))
        page_number = int(page_number)
        page_size = int(page_size)

        date = get_next_open_date(datetime.datetime.today())

        embed = mensa_embed_builder(mensa, date)
        embed.set_thumbnail(url=mensa["thumbnail"])
        embed.description = f'Menu for the {mensa.get("display_name", "")} mensa. Provided by the [eat-api](https://tum-dev.github.io/eat-api/).' + (f" Notice: this menu is for _{date.strftime('%A')}_!" if datetime.datetime.today() != date else " Enjoy!")

        dishes_today = await mensa_api.get_dishes_for_date(mensa, date)

        pages = len(dishes_today) // page_size
        index = page_size * page_number

        if page_number < 1 or page_number > pages:
            return
        
        for dish in dishes_today[index:index+page_size]:
            embed.add_field(name=dish.get("name", "?") + " " + dish.get("emoji", "") , value=f'`{dish["dish_type"]}` €{dish["prices"]["students"]["price_per_unit"]} / {dish["prices"]["students"]["unit"]}\n\n{" ".join(map(lambda x : f"`{mensa_api.LABELS.get(x)}`", dish["labels"]))}', inline=True)
        embed.set_footer(text=f"Page {page_number} of {pages}")
        await ctx.send(embed=embed)

    async def labels(self, ctx):
        '''
        Sends a message containing a dictionary of labels -> meaning
        '''
        await ctx.send("\n".join(sorted([f"`{i}`: {v}" for i,v in mensa_api.LABEL_MAP.items()], reverse=True)))


    @commands.hybrid_command(brief="Mensa command")
    async def mensa(self, ctx, *, parameters=""):
        parameters = parameters.split(" ")
        if len(parameters) < 1:
            await self.info(ctx)
            return  

        command, sub_parameters = parameters[0], parameters[1:]
        f = None
        match command.lower():
            case "menu":
                f = self.menu
            case "info":
                f = self.info
            case "labels":
                f = self.labels
            case _:
                if await mensa_api.mensa_from_string(command):
                    sub_parameters = [command]
                else:
                    sub_parameters = ["garching"]
                f = self.info
            
        await f(ctx, *sub_parameters)


    @commands.hybrid_command(brief="get a simple graph of the mensa usage")
    async def mensaplot(self, ctx, dayofweek: int = -1):
        if dayofweek == -1:
            dayofweek = datetime.datetime.today().weekday()
        df = pd.read_csv(self.bot.config.mensa_csv, names=["time", "count"], dtype={"time": float, "count": int})
        df['time'] = pd.to_datetime(df['time'], unit="s").dt.tz_localize('UTC').dt.tz_convert('Europe/Berlin')
        df = df.set_index("time")
        df = df.resample("1min").sum()
        df = df.loc[(df.index.dayofweek == dayofweek) & (df.index.hour > 9) & (df.index.hour < 16)]
        df["date"] = df.index.date
        df["clocktime"] = df.index.time
        dfw = df
        dfw.reset_index(drop=True, inplace=True)
        fig = px.line(dfw, x="clocktime", y="count", color="date")
        img = io.BytesIO()
        fig.write_image(img, format="png", scale=3)
        img.seek(0)
        await ctx.channel.send(file=discord.File(fp=img, filename="yeet.png"))

    def cog_unload(self):
        self.update_channel.cancel()

    @tasks.loop(minutes=5)
    async def update_channel(self):
        log.info("Running scheduled task")
        channels = list(filter(lambda x: str(x.id) in self.bot.config.mensa_channel, list(self.bot.get_all_channels())))
        if len(channels) < 1:
            return

        mensa = await mensa_api.mensa_from_string("arcisstr")
        occupation = await mensa_api.get_occupancy(mensa)

        for channel in channels:
            await channel.edit(name=f'Mensa {(mensa["display_name"]).capitalize()}: {int(occupation)} 👥')


def setup(bot):
    return bot.add_cog(Mensa(bot))
