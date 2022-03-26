#! /bin/python3.10
import asyncio
import sys
import discord
from discord.ext import commands
from uwubot import UwuBot


def main():
    config_file = "owobot/owo.toml"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    bot = UwuBot(config_file)
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start())

    loop.run_forever()


if __name__ == '__main__':
    main()
