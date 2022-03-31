#!/bin/python3
import sys
from owobot import OwOBot


def main():
    config_file = "owobot/owo.toml"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    bot = OwOBot(config_file)
    bot.run()


if __name__ == '__main__':
    main()
