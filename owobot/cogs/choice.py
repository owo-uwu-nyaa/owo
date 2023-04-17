import datetime
import io
import logging
import random

import re
import discord
from discord import app_commands
import pandas as pd
import plotly.express as px
from discord.ext import tasks, commands

import math
from owobot.owobot import OwOBot

class Choice(commands.Cog):
    def __init__(self, bot: OwOBot):
        self.bot = bot
        self.exclusionEntries = {}
        self.votes = {}

    async def choice(self, ctx):
        pass

    @commands.hybrid_command()
    async def random(self, ctx, *, parameters=""):
        parameters = list(set([s.strip() for s in parameters.split(",") if re.match("[\S]", s.strip())]))
        if len(parameters) < 1:
            return
        
        await ctx.send(f"I choose: `{random.choice(parameters)}`")

    @commands.hybrid_group()
    async def exclusion(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @exclusion.command(name="create", brief="randomly pick from choices")
    async def c(self, ctx, *, parameters = ""):
        parameters = list(set([s.strip().lower() for s in parameters.split(",") if re.match("[\S]", s.strip())]))
        if len(parameters) < 1:
            return
    
        self.exclusionEntries[ctx.channel.id] = parameters
        await ctx.send("Created poll with `" + ", ".join(parameters) + "`")
        
    @exclusion.command(name="pop", brief="randomly pick from choices")
    async def pop(self, ctx, *,target=""):
        parameters = self.exclusionEntries.get(ctx.channel.id)
        if not parameters:
            return
        
        try:
            parameters.remove(target.lower())
            await ctx.send(f"Removed `{target.lower()}`, please pop another value: `{', '.join(parameters)}`")
        except:
            return
            
        if len(parameters) == 1:
            await ctx.send(f"🥇 List empty, `{parameters[0]}` wins by exclusion.")
    
    @commands.hybrid_group()
    async def poll(self, ctx):
        if ctx.invoked_subcommand is None:
            parameters = self.votes.get(ctx.channel.id)
            if not parameters:
                await ctx.send(f"No current poll on this channel. Create one with the `{self.bot.command_prefix}poll create` command!")
                return
            await ctx.send("Current poll: `" + ", ".join(parameters) + "`")

    @poll.command(name="create", brief="randomly pick from choices")
    async def create(self, ctx, *, parameters = ""):
        parameters = {s.strip().lower():0 for s in parameters.split(",") if re.match("[\S]", s.strip())}
        if len(parameters) < 1:
            return
    
        self.votes[ctx.channel.id] = parameters
        await ctx.send("Created poll with `" + ", ".join(parameters) + "`")
        
    @poll.command(name="vote", brief="randomly pick from choices")
    async def vote(self, ctx, *, target=""):
        target = target.lower()
        parameters = self.votes.get(ctx.channel.id)
        if not parameters:
            return
                
        value = parameters.get(target)
        if value is None:
            await ctx.send("Could not find an item to vote for, please pick from `" + ", ".join(parameters) + "`")

            return
        
        self.votes[ctx.channel.id][target] = value + 1
        
        await ctx.send(f"{ctx.author.name}, voted for `{target}`, current votes: `{value + 1}`")
        
    @poll.command(name="results", brief="randomly pick from choices")
    async def results(self, ctx):
        parameters = self.votes.get(ctx.channel.id)
        if not parameters:
            return
        
        maxVotes, winner = 0, None
        tied = set()
        for item, votes in parameters.items():
            if votes >= maxVotes:
                if votes == maxVotes:
                    tied.add(item)
                    if winner:
                        tied.add(winner)
                        winner = None
                    
                else:
                    tied = set()
                    winner = item
                    maxVotes = votes

        tied = list(tied)
        result = ""
        if winner:
            result = f"🥇 Current winner is `{winner.lower()}` with `{maxVotes}` votes. "
        else:
            result = "Hm... No winner could be decided."
            if len(tied) > 0:
                result += " Tied between `" + ", ".join(tied) + f"` with {maxVotes} votes."

        leaderboard = sorted([(i, v) for i, v in parameters.items()], key=lambda a: a[1], reverse=True)
        result += "\n```\n" + "\n".join([f"[{i+1}] {item[0]}: {item[1]} votes" for i, item in enumerate(leaderboard)])
        result += "```"
        await ctx.send(result)

def setup(bot):
    return bot.add_cog(Choice(bot))
