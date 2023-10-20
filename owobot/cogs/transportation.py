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

SEVERITY = {
    "Major Disruption" : (8, "🔴", 0xDD2E44),
    "Fahrtausfälle" : (7, "🔴", 0xDD2E44),
    "Verspätungen" : (6, "🟠", 0xF4900B),
    "Umleitung" : (5, "🟠", 0xF4900B),
    "Bauarbeiten" : (4, "🟠", 0xF4900B),
    "Betriebsstörung" : (3, "🟡", 0xFDCB58),
    "Unregelmäßigkeiten" : (2, "🟡", 0xFDCB58),
    "Disruption" : (1, "🔵", 0x5EAEEC)
}

MVG_BASEURL = "https://www.mvg.de/api"
LOCATION_ENDPOINT = "/fib/v2/location"
DEPARTURE_ENDPOINT = "/fib/v2/departure?globalId={globalId}&limit=15&offsetInMinutes=02"
#&transportTypes=UBAHN,BUS
MESSAGE_ENDPOINT = "/fib/v2/message?messageTypes=INCIDENT"
WARNING_ENDPOINT = "/ems/tickers"

CLEANR = re.compile('<.*?>') 


def cleanhtml(raw_html):
    
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext

def get_lines(warning):
    return set(map(lambda line: "`"+line.get("name")+"`",warning.get("lines")))
        
        
def create_embed_for_station(station, departures=[], warnings=[]):
    embed = discord.Embed()

    if len(departures) > 0:
        departure_text = ""# station_data.get("name") + " - " + (", ".join(station_data.get("transportTypes"))) + "\n"
        for i in range(1,6):
            if i > len(departures):
                break
            data = departures[i]

            departure_time = int(data['plannedDepartureTime'] / 1000)#datetime.datetime.fromtimestamp()
            # t = departure_time.strftime('%H:%M')
            departure_text += f"<t:{departure_time}:t> `{data.get('label')}` {data.get('destination')} (<t:{departure_time}:R>) \n"
        embed.add_field(name="Next departures", value=departure_text, inline=False)    
        
    description = "`"+", ".join(station.get("transportTypes"))+"`"
    print(warnings)
    if len(warnings) > 0:
        print("hi", len(warnings))

        highest_warning = get_highest_severity_warning(warnings)
        highest_severety = highest_warning.get('severity')
        description += f"\n\n{SEVERITY[highest_severety][1]} {highest_severety}: There are {len(warnings)} active disruption(s) for this station."
        embed.add_field(name="Disruptions", value="\n".join(map(lambda w: w.get("title"),warnings)), inline=False)    


    embed.title = station.get('name') + ", " + station.get("place")
    embed.description = description
    embed.set_thumbnail(url="https://www.mvg.de/dam/jcr:6d13d308-c31f-4308-a964-3f1e45d000ac/Open_Graph_MVG_Fahrinfo_Muenchen.png")
    embed.color = 0x4563a3
    
    embed.set_image(url=f"https://www.mvv-muenchen.de/fileadmin/bis/Bilder/Architektur/{station.get('divaId'):04d}_1.jpg")
    embed.set_footer(text= "Last updated on " + datetime.datetime.now().strftime("%A %Y/%m/%d %H:%M"))

    
    
    return embed

def get_highest_severity_warning(warnings):
    highest_level, highest_severity_name, highest_warning = 0, "Disruption", None
    for warning in warnings:
        severity_name = get_severity_level(warning)
        severity = SEVERITY[severity_name]
        severity_level = severity[0]
        if severity_level > highest_level:
            highest_level = severity_level
            highest_warning = warning
            highest_severity_name = severity_name

    highest_warning["severity"] = highest_severity_name
    return highest_warning

def get_severity_level(warning, lines=None):
    severity_name, level = "Disruption", 0
    for needle, severity_level in SEVERITY.items():
        if needle.lower() in warning.get("text").lower() or needle.lower() in warning.get("title").lower() and severity_level[0] > level:
            severity_name = needle

    if lines is not None and len(lines) > 5:
        severity_name = "Major Disruption"

    return severity_name

def create_embed_for_warning(warning):
    info = warning.get("text").split("<br/>")
    if len(info) > 5:
        info = "\n".join(info[0:4])
    else:
        info = "\n".join(info)

    lines = get_lines(warning)
    severity_name = get_severity_level(warning, lines) 
    txt = ", ".join(lines) 
    if len(lines) > 5:
        txt = "`Multiple lines`"

    embed = discord.Embed()
    embed.description = f"[{warning.get('type')}] - Münchner Verkehrsgesellschaft"
    embed.color = SEVERITY[severity_name][2]
    embed.set_thumbnail(url="https://www.mvg.de/dam/jcr:6d13d308-c31f-4308-a964-3f1e45d000ac/Open_Graph_MVG_Fahrinfo_Muenchen.png")
    embed.add_field(name=f"{SEVERITY[severity_name][1]} {severity_name.capitalize()} " + txt + " " + warning.get("title", "?"), value=cleanhtml(unescape(info)), inline=False)    
    embed.add_field(name=f"Affected lines", value=", ".join(lines), inline=False)    

    embed.set_footer(text="Last updated on " + datetime.datetime.now().strftime("%A %Y/%m/%d %H:%M"))

    return embed

def stationInLines(globalId, lines):
    print("searching", globalId, lines)
    for line in lines:
        result = stationInLine(globalId, line)
        if result is True:
            return True
    return False

def stationInLine(globalId, line):
    for station in line.get("stations"):
        print(station.get("name"), station.get("id"), globalId)
        if globalId == station.get("id"):
            print("found", station.get("name"))
            return True
    return False
    

class Transportation(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot
        self.update_channel.start()
        self.fetch_warning.start()

    def get_warning_from_mvg(self):
        response = requests.get(MVG_BASEURL+WARNING_ENDPOINT)
        assert(response.ok)
        return response.json()
    
    def get_warnings_for_station(self, globalId, includePlanned=False):
        warnings =  dict()
        try:
            # Process warnings to ignore planned events 
            #x["type"] != "PLANNED"
            # x.get("type") != "PLANNED"
            for warnung in filter(lambda x : x.get("type") and x.get("text") and stationInLines(globalId, x.get("lines")) and (True if includePlanned else x.get("type") != "PLANNED"), self.get_warning_from_mvg()):
                id = warnung.get("id")
                print(get_lines(warnung),warnung.get("title") )
                warnings[id] = warnung
        except:
            print("meow")

        return warnings
    
    def get_warnings(self, includePlanned=False):
        warnings =  dict()
        try:
            # Process warnings to ignore planned events 
            #x["type"] != "PLANNED"
            # x.get("type") != "PLANNED"
            for warnung in filter(lambda x : x.get("type") and x.get("text") and (True if includePlanned else x.get("type") != "PLANNED") , self.get_warning_from_mvg()):
                id = warnung.get("id")
                warnings[id] = warnung
        except:
            print("meow")

        return warnings
    
    def query_station_name(self, query):
        response = requests.get(MVG_BASEURL+LOCATION_ENDPOINT+"?query="+query.strip())
        assert(response.ok)

        locations = list(filter(lambda l:  l.get("type") == "STATION",response.json()))
        if len(locations) < 1:
            print("no locations found")
            return
        
        return locations[0]

    def get_departures(self, globalId):
        req = requests.get(MVG_BASEURL+DEPARTURE_ENDPOINT.format(globalId=globalId))
        if not req.ok:
            log.warn("Something went wrong")
            print(req.status_code, req.text, req.raw)
            return
        
        return sorted([d for d in req.json()], key=lambda x:x['plannedDepartureTime'])

    @commands.hybrid_command(brief="Fetches and displays current MVG disruptions")
    async def mvg(self, ctx):
        warnings = self.get_warnings(includePlanned=False)
        count = len(warnings)
        text = f'There are `{count}` disruption(s) registered by MVG.\n'

        value = 0

        i = 0
        for _, warning in warnings.items():
            if i > 10:
                text += f"\n... {count-10} more warnings in https://www.mvg.de/dienste/betriebsaenderungen.html "
                break
            
            lines = get_lines(warning)

            disruption_level = get_severity_level(warning, lines)
            severity = SEVERITY[disruption_level]

            value+=severity[0]
            text += f"- {severity[1]} " + ", ".join(lines) + " " + warning.get("title")  + "\n"

            i += 1
            
        text += f"Disruption Value: {value}"            
        await ctx.channel.send(content=text)

    @commands.hybrid_command(brief="Fetches information about station")
    async def station(self, ctx, *,name):
        station_data = self.query_station_name(name)
        if station_data is None:
            await ctx.send("No stations found with this name :(")
            return
        
        global_id = station_data.get("globalId")

        departures = self.get_departures(global_id)
        if departures is None:
            return
        
        warnings = self.get_warnings_for_station(global_id).values()

        await ctx.send(content=f"`{global_id}`",embed=create_embed_for_station(station_data, departures, list(warnings)))

        # warning = get_highest_severity_warning(warnings)
        # await ctx.send(embed=create_embed_for_warning(warning))



    @tasks.loop(seconds=300)
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

        departures = self.get_departures("de:09184:460") # Garching Forschungszentrum: de:09184:460
        if departures is None:
            return
        
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

