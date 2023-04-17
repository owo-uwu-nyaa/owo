import datetime
import io
import logging
import math
import random
import re

import discord
import pandas as pd
import plotly.express as px
from discord import app_commands
from discord.ext import commands, tasks
import requests

from owobot.owobot import OwOBot

ENDPOINT = "https://www.mvg.de/api/fib/v2/departure?globalId=de:09184:460&limit=15&offsetInMinutes=00&transportTypes=UBAHN,BUS"

class Transportation(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot
        self.update_channel.start()

    @tasks.loop(seconds=6)
    async def update_channel(self):
        channels = list(
            filter(
                lambda x: str(x.id) in self.bot.config.transport_channels,
                list(self.bot.get_all_channels()),
            )
        )
        if len(channels) < 1:
            return
        
        req = requests.get(ENDPOINT)
        assert(req.ok)
        departures = sorted([d for d in req.json()], key=lambda x:x['plannedDepartureTime'])

        message = ""
        for i in range(1,3):
            if i > len(departures):
                break
            data = departures[i]

            departure_time = datetime.datetime.fromtimestamp(data['plannedDepartureTime'] / 1000)
            message += f"[{data.get('label')}] {departure_time.strftime('%H:%M')} "
            
        
        for channel in channels:
            await channel.edit(name=message)

            


def setup(bot):
    return bot.add_cog(Transportation(bot))

