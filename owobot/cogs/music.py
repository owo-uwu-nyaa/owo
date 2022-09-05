import itertools
import logging
import re
from multiprocessing import Process
from discord.ext import commands
from owobot.misc import common
import yt_dlp

from owobot.misc.database import MusicChan

log = logging.getLogger(__name__)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.folder = bot.config.dl_folder

    async def cog_check(self, ctx):
        return await common.is_owner(ctx)

    @staticmethod
    def download_audio(link: str, folder: str, playlist: str):
        outtmpl = "%(title)s.%(ext)s"
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{folder}/{outtmpl}",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "best",
                    "preferredquality": "best",
                },
                {
                    "key": "FFmpegMetadata",
                    "add_chapters": True,
                    "add_metadata": True,
                },
            ],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(link)
            info = ydl.extract_info(link)
            title = ydl.evaluate_outtmpl("%(title)s", info)
            with open(f"{folder}/{playlist}.m3u", "a") as pl:
                pl.write(f"{title}.opus\n")

    @commands.hybrid_command()
    async def dl(self, ctx, url: str):
        p = Process(
            target=self.download_audio, args=(url, self.folder, str(ctx.author.id))
        )
        p.start()
        # we should actually wait for the process and react accordingly
        await common.react_success(ctx)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.webhook_id is not None:
            return
        if (
            not MusicChan.select()
            .where(MusicChan.channel == message.channel.id)
            .exists()
        ):
            return
        content = message.content
        links = re.findall(r"([^ ]*youtu.be/[^ ]*)|([^ ]*youtube.com/[^ ]*)", content)
        for link in filter(lambda l: l != "", itertools.chain(*links)):
            p = Process(
                target=self.download_audio,
                args=(link, self.folder, str(message.author.id)),
            )
            p.start()


def setup(bot):
    return bot.add_cog(Music(bot))
