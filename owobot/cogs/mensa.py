import datetime
import io
import random

import discord
import pandas as pd
import plotly.express as px
import requests
from discord.ext import tasks, commands

from owobot.owobot import OwOBot

MENSA_LIST = {    
    "GARCHING" : {
        "graphite" : "ap.ap*-?mg*.ssid.*",
        "menu" : "mensa-garching"
    },
    "ARCISSTR" : {
        "graphite" : "ap.ap*-?bn*.ssid.*",
        "menu" : "mensa-arcisstr"
    },
    "LEOPOLDSTR" : {
        "graphite" : "ap.ap*-?lm*.ssid.*",
        "menu" : "mensa-leopoldstr"
    },
    "MARTINSRIED" : {
        "graphite" : "ap.ap*-?ij*.ssid.*",
        "menu" : "mensa-martinsried"
    }
}

async def get_stats(mensa):
    return requests.get(f"http://graphite-kom.srv.lrz.de/render/?from=-1h&target={MENSA_LIST[mensa]['graphite']}&format=json").json()

async def getMenu(id, year, week):
    return requests.get(f"https://tum-dev.github.io/eat-api/{id}/{year}/{week}.json")

async def getDishes():
    year, week = datetime.today().year, datetime.today().strftime("%U")
    data = await getMenu("mensa-garching", year, week).json()
    for day in data["days"]:
        print(day["date"])
        for dish in day["dishes"]:
            print("-",dish["name"])

async def get_occupancy(mensa):
    page = await get_stats(mensa)

    aps = list(map(lambda x: (x['target'].split('.')[1], x['datapoints'][-1][0] or x['datapoints'][-2][0] or 0), page))
    stats = dict()
    for ap, current in aps:
        if ap in stats:
            stats[ap] += current
        else:
            stats[ap] = current

    return sum(stats.values())


class Mensa(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot
        self.update_channel.start()

    @commands.hybrid_command(brief="see how many people are at the mensa")
    async def mensa(self, ctx):
        stats = requests.get("http://mensa.liste.party/api").json()
        await ctx.send(
            f"Gerade wuscheln {stats['current']} Menschen in der Mensa. Das ist eine Auslastung von {stats['percent']:.0f}%")



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

    @tasks.loop(seconds=30)
    async def update_channel(self):
        print("running schedule task")
        channels = list(filter(lambda x: x.id == self.bot.config.mensa_channel, list(self.bot.get_all_channels())))
        if len(channels) < 1:
            return
        channel = channels[0]
        print(channel)
        mensa = "GARCHING"
        occupation = await get_occupancy(mensa)
        await channel.edit(name=f"Mensa {mensa.lower().capitalize()}: {int(occupation)} :busts_in_silhouette:")


def setup(bot):
    return bot.add_cog(Mensa(bot))
