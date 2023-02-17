import datetime
import io
import random

import discord
import pandas as pd
import plotly.express as px
import requests
from discord.ext import tasks, commands

from owobot.owobot import OwOBot
from owobot.misc import mensa_api

class Mensa(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot
        self.update_channel.start()

    @commands.hybrid_command(brief="see mensa stats")
    async def mensa(self, ctx, mensa="garching"):
        mensa = await mensa_api.mensa_from_string(mensa)
        if not mensa:
            return await ctx.send("Please select one of the following canteens: " + ", ".join(mensa_api.MENSA_LIST.keys()))

        dishes = await mensa_api.get_dishes_for_today(mensa)

        embed = discord.Embed(
            title=f'{mensa["display_name"]} / {datetime.datetime.today().strftime("%Y-%m-%d")}',
            color=0x3edb53
        )
        
        for dish in list(filter(lambda dish : dish["dish_type"] != "Beilagen", dishes)):
            dish_name = dish["name"]
            dish_short = None
            if "mit" in dish_name:
                tbl = dish_name.split(" mit ")
                dish_short = tbl[0]
                #\n{" ".join(map(lambda x : mensa_api.LABELS.get(x), dish["labels"]))}\n
                #{dish_name if dish_short else ""}\n
            display_name = dish_short if dish_short else dish_name
            embed.add_field(name=display_name + " " + mensa_api.TYPES.get(dish["dish_type"]), value=f'`{dish["dish_type"]}` €{dish["prices"]["students"]["price_per_unit"]} / {dish["prices"]["students"]["unit"]}', inline=True)

        await ctx.send(embed=embed)

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
        self.printer.cancel()

    @tasks.loop(minutes=1)
    async def update_channel(self):
        print("running scheduled task")
        channels = list(filter(lambda x: str(x.id) in self.bot.config.mensa_channel, list(self.bot.get_all_channels())))
        if len(channels) < 1:
            return

        mensa = await mensa_api.mensa_from_string("Garching")
        occupation = await mensa_api.get_occupancy(mensa)

        for channel in channels:
            await channel.edit(name=f'Mensa {(mensa["display_name"]).capitalize()}: {int(occupation)} 👥')


def setup(bot):
    return bot.add_cog(Mensa(bot))
