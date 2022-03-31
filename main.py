#!/bin/python3
import logging
import os
import sys
from owobot.owobot import OwOBot


def main():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    config_file = "owobot/owo.toml"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    bot = OwOBot(config_file)
    bot.run()


if __name__ == '__main__':
    main()
