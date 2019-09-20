## Installation

The scripts requires at least Python 3.7. Example install on Ubuntu:

```shell script
sudo apt update
sudo apt install python3.7
```

Then, create a virtual environment just for this project:

```shell script
python3.7 -m venv ~/scripts/twitch-reddit-bot/venv
```  

Make sure the dependencies (`Requests` and `PRAW`) are installed:
```shell script
source ~/scripts/twitch-reddit-bot/venv/bin/activate
pip install requests praw
deactivate
```

When you launch the script make sure to use a full path to this Python instance. Especially important when setting a cronjob.

```shell script
~/scripts/twitch-reddit-bot/venv/bin/python3 bot.py

## Purpose of each Bot

# Projared

Master of all bots - Will handle all requests

# JumJumJr

Grabs the latest stream information and writes it to a file

# Nuptup

I don't fucking know

# Dieth-Woodrow

Will update when I actually read the damn thing

