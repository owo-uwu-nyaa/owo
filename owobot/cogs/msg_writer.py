import csv
import threading
import time

from discord.ext import commands


class MsgWriter(commands.Cog):

    def __init__(self, bot, config):
        self.bot = bot
        self.csvfile = open(config.message_file, 'a', newline='')
        self.msgwriter = csv.writer(self.csvfile, quoting=csv.QUOTE_MINIMAL)
        self.csv_writer_lock = threading.Lock()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        with self.csv_writer_lock:
            self.msgwriter.writerow([message.id, message.author.id, message.channel.id, message.guild.id, time.time(), message.content])
            self.csvfile.flush()
