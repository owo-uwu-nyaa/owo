import contextlib
import io
import os

os.environ[
    "PYSPARK_SUBMIT_ARGS"
] = "--packages org.apache.kudu:kudu-spark3_2.12:1.15.0 pyspark-shell"
from pathlib import Path
import discord
from discord.ext.commands import Bot
from owobot.misc.config import Config
import logging

log = logging.getLogger(__name__)


class OwOBot(Bot):

    def __init__(self, config_path, *args, **options):
        config = Config(config_path)

        intents = discord.Intents().all()
        allowed_mentions = discord.AllowedMentions(
            users=True, everyone=False, roles=False, replied_user=False
        )
        super().__init__(
            *args,
            command_prefix=config.command_prefix,
            description=config.desc,
            intents=intents,
            allowed_mentions=allowed_mentions,
            **options
        )
        self.config = config
        self._token = config.discord_token

        async def load_cogs():
            total, skipped, errors, ok = 0, 0, 0, 0
            for file in (Path(__file__).parent / "cogs").iterdir():
                cog_name = file.stem

                if not cog_name.startswith("_") and file.suffix == ".py" and file.is_file():
                    total += 1
                else:
                    continue

                if cog_name in config.blocked_cogs:
                    log.info(f"skipped loading blocked cog {cog_name}")
                    skipped += 1
                    continue

                stdout, stderr = None, None
                try:
                    stdout, stderr = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
                        await self.load_extension(f"owobot.cogs.{cog_name}")
                    log.info(f"loaded cog '{cog_name}'")
                    log.debug(str(stdout))
                    log.debug(str(stderr))
                    ok += 1
                except Exception as e:
                    log.error(f"Could not load cog '{cog_name}' from {file}: {e}")
                    log.error(str(stdout))
                    log.error(str(stderr))
                    errors += 1

            log.info(f"done loading cogs (skipped = {skipped}, errors = {errors}, ok = {ok} out of {total} found cog(s))")

        self._load_cogs = load_cogs

    async def setup_hook(self):
        await self._load_cogs()

    def run(self, **kwargs):
        log.info("starting bot")
        super().run(self._token, reconnect=True, **kwargs)
