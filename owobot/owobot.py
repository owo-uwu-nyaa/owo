import contextlib
# import functools
import io
import os
import ssl
from pathlib import Path
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
import heapq
from typing import NamedTuple

import discord
from discord.ext import tasks
from discord.ext.commands import Bot, Command
from owobot.misc.config import Config
import logging

from typing import MutableMapping
from httpx import AsyncClient
from aiohttp import web


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
            **options,
        )
        self.config = config
        self._token = config.discord_token

        async def load_cogs():
            print("Lowoading!")
            total, skipped, errors, ok = 0, 0, 0, 0
            for file in (Path(__file__).parent / "cogs").iterdir():
                cog_name = file.stem

                if (
                    not cog_name.startswith("_")
                    and file.suffix == ".py"
                    and file.is_file()
                ):
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

            log.info(
                f"done loading cogs (skipped = {skipped}, errors = {errors}, ok = {ok} out of {total} found cog(s))"
            )

        self._load_cogs = load_cogs

        # httpx client
        self.http_client = AsyncClient()

        # aiohttp server
        self.http_app = web.Application()
        self._aiohttp_runner = None
        self._ssl_site = None
        self._no_ssl_site = None

        self._dynamic_commands: MutableMapping[discord.PartialMessage, OwOBot.dynamic_command] = dict()

    dynamic_command = NamedTuple("dynamic_command", [("timestamp", datetime), ("name", str)])

    def handle_dynamic(self, msg: discord.PartialMessage, name=None):
        self._dynamic_commands[msg] = OwOBot.dynamic_command(timestamp=datetime.now(timezone.utc), name=name)

    def check_dynamic(self, msg: discord.PartialMessage):
        return self._dynamic_commands.pop(msg, None)

    @tasks.loop(minutes=10)
    async def _cleanup_handled_dynamic_commands(self):
        now = datetime.now(timezone.utc)
        for msg, cmd in self._dynamic_commands.items():
            if now - cmd.timestamp > timedelta(minutes=1):
                self._dynamic_commands.pop(msg)
                log.warning(f"dynamic command was handled, but no error handler processed it (from message {msg.id})")

    command_suggestion = NamedTuple("command_suggestion", [("command", Command), ("name", str), ("ratio", float)])

    def suggest_commands(self, text, n=3, cutoff=0.6):
        result = []
        s = SequenceMatcher()
        s.set_seq2(text)
        for cmd_or_group in self.commands:
            best_ratio, best_name = None, None
            for name in (cmd_or_group.name, *cmd_or_group.aliases):
                min_ratio = cutoff if best_ratio is None else best_ratio
                s.set_seq1(name)
                if (
                    s.real_quick_ratio() >= min_ratio
                    and s.quick_ratio() >= min_ratio
                    and s.ratio() >= min_ratio
                ):
                    best_ratio, best_name = s.ratio(), name
            if best_ratio is not None:
                result.append(OwOBot.command_suggestion(command=cmd_or_group, name=name, ratio=best_ratio))

        return heapq.nlargest(n, result, key=lambda suggestion: suggestion.ratio)

    async def setup_hook(self):
        await self._load_cogs()

        self._aiohttp_runner = web.AppRunner(self.http_app)
        await self._aiohttp_runner.setup()

        if self.config.http_ssl:
            # CLIENT_AUTH: authenticate clients, i.e. operate as a server
            ssl_ctx = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            ssl_ctx.load_cert_chain(self.config.http_ssl_certfile, self.config.http_ssl_keyfile)

            self._ssl_site = web.TCPSite(
                self._aiohttp_runner,
                host=self.config.http_hostname,
                port=self.config.http_ssl_port,
                ssl_context=ssl_ctx
            )
            await self._ssl_site.start()

        if self.config.http_no_ssl:
            self._no_ssl_site = web.TCPSite(
                self._aiohttp_runner,
                host=self.config.http_hostname,
                port=self.config.http_no_ssl_port,
            )
            await self._no_ssl_site.start()

    def run(self, **kwargs):
        log.info("starting bot")
        super().run(self._token, reconnect=True, **kwargs)
