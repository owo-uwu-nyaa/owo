from __future__ import annotations

import logging
import contextlib
from os import path, environ
import functools as ft
import toml
import yarl
from peewee import PostgresqlDatabase, SqliteDatabase
from playhouse.migrate import PostgresqlMigrator, SqliteMigrator
from owobot.misc import database
from collections.abc import Mapping
from typing import TypeVar

log = logging.getLogger(__name__)


class MissingKeyException(KeyError):
    pass


def _get_mapping_key(mapping, *key_path):
    """get value in nested mapping at path, or None"""
    return ft.reduce(lambda m, k: m.get(k, None) if isinstance(m, Mapping) else None, key_path, mapping)


def _get_key(user, default, *key_path):
    env_key = ".".join(("owo", *key_path))
    # find key in user config, then environment, then default config
    for mapping, kp in [(user, key_path), (environ, [env_key]), (environ, [env_key.upper()]), (default, key_path)]:
        if (value := _get_mapping_key(mapping, *kp)) is not None:
            return value

    raise MissingKeyException(".".join(key_path))


#TODO rewrite this to be configured automatically
class Config:
    def __init__(self, config_file: str):
        try:
            self.config = toml.load(open(config_file, mode="r", encoding="utf-8"))
        except OSError as e:
            log.critical(f"unable to open config file {config_file}: {e}")
        except (TypeError, toml.TomlDecodeError) as e:
            log.critical(f"invalid config file: {e}")
        src_dir, _ = path.split(path.realpath(__file__))
        default_config_file = path.join(src_dir, "../../owo.toml")
        self.default_config = None
        if not path.samefile(config_file, default_config_file):
            try:
                self.default_config = toml.load(
                    open(default_config_file, mode="r", encoding="utf-8")
                )
            except OSError as e:
                log.error(
                    f"unable to open default config file {default_config_file}: {e}"
                )
            except (TypeError, toml.TomlDecodeError) as e:
                log.error(f"invalid default config file: {e}")

        self.command_prefix = str(self.get_key("command_prefix"))
        self.desc = str(self.get_key("desc"))
        self.blocked_cogs = []
        if self.has_toplevel_key("blocked_cogs"):
            self.blocked_cogs = list(map(str, self.get_key("blocked_cogs")))

        self.left_emo = str(self.get_key("navigation", "left_emo"))
        self.right_emo = str(self.get_key("navigation", "right_emo"))
        self.up_emo = str(self.get_key("navigation", "up_emo"))
        self.down_emo = str(self.get_key("navigation", "down_emo"))

        self.dl_folder = str(self.get_key("music", "dl_location"))

        self.mensa_csv = str(self.get_key("mensa", "historyfile"))

        self.catapi_token = str(self.get_key("api_tokens", "catapi"))
        self.discord_token = str(self.get_key("api_tokens", "discord"))

        if self.has_toplevel_key("postgres"):
            try:
                db = PostgresqlDatabase(
                    str(self.get_key("postgres", "db")),
                    user=str(self.get_key("postgres", "user")),
                    host=str(self.get_key("postgres", "host")),
                    autorollback=True,
                )
                database.set_db(db, PostgresqlMigrator(db))
                log.info("Using postgres as DB")
            except Exception as e:
                log.error(
                    f"Could not connect to Postgres: {e}\n Some Cogs may not work properly, continuing...\n"
                )
        elif self.has_toplevel_key("sqlite"):
            db = SqliteDatabase(
                path.join(str(self.get_key("sqlite", "dir")), "owo.sqlite")
            )
            database.set_db(db, SqliteMigrator(db))
            log.info("Using sqlite as DB")

        self.datalake = None
        if self.has_toplevel_key("csv"):
            from owobot.misc import datalake
            self.datalake = datalake.CSVDataLake(self.get_key("csv", "dir"))
            log.info("Using CSV as Datastore")

        self.http_hostname = self.get_key("http", "hostname")

        self.http_ssl = self.get_key("http", "ssl", default=True)
        self.http_no_ssl = self.get_key("http", "no_ssl", default=False)
        if self.http_ssl:
            self.http_ssl_port = self.get_key("http", "ssl_port")
            self.http_ssl_certfile = self.get_key("http", "certfile")
            self.http_ssl_keyfile = self.get_key("http", "keyfile", default=None)
        if self.http_no_ssl:
            self.http_no_ssl_port = self.get_key("http", "no_ssl_port")

        if not self.http_ssl and not self.http_no_ssl:
            log.warning(f"http.ssl and http.no_ssl are both set to false; no server will be started")
        if self.http_ssl and self.http_no_ssl and self.http_ssl_port == self.http_no_ssl_port:
            raise ValueError("http.ssl_port and http.no_ssl_port must be different")

        self.http_url = self.get_key("http", "url", default=None)
        if self.http_url is not None:
            self.http_url = yarl.URL(self.http_url)

    _missing = object()
    T = TypeVar("T")

    def get_key(self, *key_path: str, default: T = _missing) -> str | list[str] | T:
        # if default is given, supress MissingKeyException and return default instead
        with contextlib.suppress(*() if default is Config._missing else (MissingKeyException,)):
            return _get_key(self.config, self.default_config, *key_path)
        return default

    def __getitem__(self, item):
        return self.get_key(*item)

    def has_toplevel_key(self, key):
        return key in self.config
