# owo 😝

## Requirements

- a moderately up-to date version of Python3
- optional: a postgres database (default alternative: sqlite)
- optional: apache kudu (default alternative: csv)

## Setup

1.  install requirements via `pip install -r requirements.txt`
    (pip3 if using something like debian)

    ```bash
    # Install requirements
    pip install -r requirements.txt
    ```

1.  edit owo.toml to your liking - at minimum you should provide a discord
    bot token

1.  run - you may pass a custom path to the configuration file as i
    the first command line argument

    ```bash
    cd owobot
    # Optionally update permissions of the script
    chmod +x main.py
    ./main.py
    ```

1.  ????
1.  profit 📈

## Notes

- may occasionally be broken on inferior platforms such as Windows and
  MacOs
