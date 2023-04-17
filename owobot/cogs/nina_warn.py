import datetime
import io
import logging
import random

from html import unescape
import requests

import re
import discord
from discord import app_commands
import pandas as pd
import plotly.express as px
from discord.ext import tasks, commands

import math
from owobot.owobot import OwOBot

NINA_BASE_URL = "https://warnung.bund.de/api31"
MOWAS_BASE_URL = "https://nina.api.proxy.bund.dev/api31/archive.mowas/"

log = logging.getLogger(__name__)

# As defined in
# http://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2.html
SEVERITY = {
    "Extreme" : (5, "🟣", 0xAA8ED6),
    "Severe" : (4, "🔴", 0xDD2E44),
    "Moderate" : (3, "🟠", 0xF4900B),
    "Minor" : (2, "🟡", 0xFDCB58),
    "Unknown" : (1, "🔵", 0x5EAEEC)
}

def create_embed_for_warning(warning):
    embed = discord.Embed()

    _info = warning.get("info")
    if _info is None:
        return

    index = 1 if len(_info) > 1 else 0 

    info = _info[index]
    msg_type = warning["msgType"]
    severity = info["severity"]

    
    effective = info.get("effective")
    expires = info.get("expires")

    expired = False
    expirationDatetime = None
    if expires:
        expirationDatetime = datetime.datetime.fromisoformat(expires)
        if datetime.datetime.now().astimezone() > expirationDatetime:
            msg_type = "Expired"
            expired = True

    embed.description = f"[{msg_type}] [{warning['status']}] - {info.get('senderName', info.get('web', '?').lower())}" + (" - **THIS IS A TEST**" if warning["status"] == "Test" else "")
    embed.color = SEVERITY[severity][2]

    embed.add_field(name=SEVERITY[severity][1] + " " + info.get("headline", "?") + (" [EXPIRED]" if expired else ""), value=unescape(info.get("description", "")).replace("<br/>","\n") + "\n"+info.get("instructions", ""), inline=False)
    if effective:
        embed.add_field(name="Effective from", value=datetime.datetime.fromisoformat(effective).strftime("%A %Y/%m/%d %H:%M"), inline=True)
    if expirationDatetime:
        embed.add_field(name="In effect until", value=expirationDatetime.strftime("%A %Y/%m/%d %H:%M"), inline=True)
    
    
    embed.set_footer(text="Last updated on " + datetime.datetime.now().strftime("%A %Y/%m/%d %H:%M"))
    return embed


class NinaWarn(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot
        self.update_channel.start()

    def get_warning_from_ars(self, code):
        response = requests.get(NINA_BASE_URL+"/dashboard/"+code+".json")
        assert(response.ok)
        return response.json()

    def get_warnings(self):
        warnings =  dict()
        for code in self.bot.config.nina_ars:
            try:
                for warnung in self.get_warning_from_ars(code):
                    id = warnung["payload"]["id"]
                    warnings[id] = warnung
            except:
                continue

            
        return warnings
 
    def get_detailed_info_from_warning_id(self, id):
        warningDetails = requests.get(NINA_BASE_URL+"/warnings/"+id+".json")
        if not warningDetails.ok:
            return None

        return warningDetails.json()

    @tasks.loop(seconds=15)
    async def update_channel(self):
        log.info("Running scheduled task")
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
            messages = [m async for m in channel.history(limit=25) if m.author == self.bot.user]
            old_messages = {}
            for m in messages:
                c = m.content.strip("`").split("@")
                if len(c) != 2:
                    continue
                id, timestamp = tuple(c)
                old_messages[id] = (m, timestamp)
                warnings[id] = {"cached": True}

            # Process new warnings, updating or replying to old messages
            for id, preliminary_warning in warnings.items():
                warning = self.get_detailed_info_from_warning_id(id)
                if warning is None and not preliminary_warning.get("cached") and id[0,4] == "mow":
                    # MOWAS alerts get archived differently, so we try again with a different endpoint
                    warningDetails = requests.get(MOWAS_BASE_URL+id+"_"+()+".json")
                    if warningDetails.ok: warning = warningDetails.json()

                previous = old_messages.get(id)
                if warning is None:
                    if previous: await previous[0].delete()
                    continue

                embed = create_embed_for_warning(warning)
                identifier = f'`{id}@{warning.get("sent","")}`'

                outdated_message = None
                if warning.get("msgType") == "Update":
                    references = warning.get("references", "").split(",")
                    if len(references) == 3:
                        _, previous_warning_id, _ = tuple(references)
                        outdated_message = old_messages.get(previous_warning_id)
                    
                # If msgType is Update and the previous warning has been found, reply to it
                if outdated_message:
                    await outdated_message.reply(content=identifier, embed=embed)
                    continue

                # If no old message with given ID is found, send a new one
                if previous is None:
                    await channel.send(content=identifier, embed=embed)
                    continue

                # If a message with the same ID exists, just update it!
                old_message, timestamp = previous
                if timestamp != warning.get("sent"):           
                    await old_message.edit(content=identifier, embed=embed)
                    
                

               

                

def setup(bot):
    return bot.add_cog(NinaWarn(bot))
