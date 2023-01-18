#!/bin/python3
import logging
import os
import sys
from owobot.owobot import OwOBot


def main():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    config_file = sys.argv[1] if len(sys.argv) == 2 else "owobot/owo.toml"
    bot = OwOBot(config_file)
    
    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')
    bot.run()

if __name__ == '__main__':
    main()
