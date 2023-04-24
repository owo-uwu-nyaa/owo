import datetime
import io
import logging
import math
import random
import re
from html import unescape

import discord
import pandas as pd
import plotly.express as px
from discord import app_commands
from discord.ext import commands, tasks
import requests

from owobot.owobot import OwOBot
log = logging.getLogger(__name__)


MVG_BASEURL = "https://www.mvg.de/api"
STATION_ENDPOINT = "/fib/v2/departure?globalId=de:09184:460&limit=15&offsetInMinutes=00&transportTypes=UBAHN,BUS"
WARNING_ENDPOINT = "/ems/tickers"

CLEANR = re.compile('<.*?>') 

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

def create_embed_for_warning(warning):
    embed = discord.Embed()


    embed.description = f"[{warning.get('type')}] - Münchner Verkehrsgesellschaft"
    embed.color = 0xDD2E44

    info = warning.get("text").split("<br/>")
    if len(info) > 3:
        info = "\n".join(info[0:2])
    embed.add_field(name="⚠ " + warning.get("title", "?"), value=cleanhtml(unescape(info)), inline=False)    
    embed.set_footer(text="Last updated on " + datetime.datetime.now().strftime("%A %Y/%m/%d %H:%M"))
    return embed

class Transportation(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot
        self.update_channel.start()
        self.fetch_warning.start()

    def get_warning_from_mvg(self):
        response = requests.get(MVG_BASEURL+WARNING_ENDPOINT)
        assert(response.ok)
        return response.json()
    
    def get_warnings(self):
        warnings =  dict()
        try:
            # Process warnings to ignore planned events 
            #x["type"] != "PLANNED"
            for warnung in filter(lambda x : x.get("type") and  x.get("type") != "PLANNED" and x.get("text"), self.get_warning_from_mvg()):
                id = warnung["id"]
                warnings[id] = warnung
                return warnings # TODO: remove this after testing
        except:
            print("meow")

        return warnings
        

    @tasks.loop(seconds=120)
    async def update_channel(self):
        log.info("Running scheduled task")

        channels = list(
            filter(
                lambda x: str(x.id) in self.bot.config.transport_channels,
                list(self.bot.get_all_channels()),
            )
        )
        if len(channels) < 1:
            return
        
        req = requests.get(MVG_BASEURL+STATION_ENDPOINT)
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

    @tasks.loop(seconds=300)
    async def fetch_warning(self):
        log.info("Running scheduled task / MVG Warning")

        channels = list(
            filter(
                lambda x: str(x.id) in self.bot.config.nina_warning_channels,
                list(self.bot.get_all_channels()),
            )
        )

        if len(channels) < 1:
            return
        
        warnings = self.get_warnings()

        for channel in channels:
            # Process old messages, see what needs to be deleted or updated!
            messages = [m async for m in channel.history(limit=25) if m.author == self.bot.user and "mvg" in m.content]
            old_messages = {}
            for m in messages:
                c = m.content.strip("`").split("@")
                if len(c) < 2: continue

                id, timestamp, *_ = tuple(c)
                if not warnings.get(id):
                    print(id, warnings)
                    await m.delete()
                else:
                    old_messages[id] = m

            for id, warning in warnings.items():
                previous = old_messages.get(id)
                if not previous:                    
                    embed = create_embed_for_warning(warning)
                    identifier = f'`{id}@{warning.get("modificationDate","")}@mvg`'
                    await channel.send(content=identifier, embed=embed)
                    warnings[id] = None


def setup(bot):
    return bot.add_cog(Transportation(bot))

