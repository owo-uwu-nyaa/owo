import logging
from os import path
import toml
from peewee import PostgresqlDatabase, SqliteDatabase
from playhouse.migrate import PostgresqlMigrator, SqliteMigrator
from owobot.misc import database

log = logging.getLogger(__name__)


class MissingKeyException(Exception):
    pass


def _get_key(user, default, *key_path):
    if user is None and default is None:
        raise MissingKeyException(*key_path)
    if len(key_path) == 0:
        return user if user is not None else default
    key = key_path[0]
    try:
        return _get_key(
            user[key] if user is not None and key in user else None,
            default[key] if default is not None and key in default else None,
            *(key_path[1:]),
        )
    except MissingKeyException as e:
        raise MissingKeyException(*key_path) from e


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
        self.mensa_channels = str(self.get_key("mensa", "target_channel_id"))
        self.nina_warning_channels = list(map(str, self.get_key("nina", "target_channel_id")))
        self.transport_channels = list(map(str, self.get_key("transportation", "target_channel_id")))
        self.nina_ars = list(map(str, self.get_key("nina", "ars")))

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

    def get_key(self, *key_path):
        return _get_key(self.config, self.default_config, *key_path)

    def has_toplevel_key(self, key):
        return key in self.config
