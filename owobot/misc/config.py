import os.path as path

import toml


class MissingKeyException(Exception):
    def __init__(self, *keys: str) -> None:
        super().__init__(*keys)


def get_key(user, default, *path):
    if user is None and default is None:
        raise MissingKeyException(*path)
    elif len(path) == 0:
        return user if user is not None else default
    else:
        key = path[0]
        try:
            return get_key(
                user[key] if user is not None and key in user else None,
                default[key] if default is not None and key in default else None,
                *(path[1:])
            )
        except MissingKeyException:
            raise MissingKeyException(*path)


class Config:

    def __init__(self, config_file: str):
        config = None
        try:
            config = toml.load(open(config_file, mode="r"))
        except OSError as e:
            print(f"unable to open config file {config_file}: {e}")
        except (TypeError, toml.TomlDecodeError) as e:
            print(f"invalid config file: {e}")
        src_dir, _ = path.split(path.realpath(__file__))
        default_config_file = path.join(src_dir, "../../owo.toml")
        default_config = None
        if not path.samefile(config_file, default_config_file):
            try:
                default_config = toml.load(open(default_config_file, mode="r"))
            except OSError as e:
                print(f"unable to open default config file {default_config_file}: {e}")
            except (TypeError, toml.TomlDecodeError) as e:
                print(f"invalid default config file: {e}")

        self.command_prefix = str(get_key(config, default_config, "command_prefix"))
        self.desc = str(get_key(config, default_config, "desc"))

        self.message_file = str(get_key(config, default_config, "messages", "file"))

        self.bottom_cmd = str(get_key(config, default_config, "bottom", "executable"))

        self.catapi_token = str(get_key(config, default_config, "api_tokens", "catapi"))
        self.discord_token = str(get_key(config, default_config, "api_tokens", "discord"))
