#! /bin/python3
import csv
import datetime
import random
import subprocess
import threading
import time
import discord
import requests
import owo
import uwu_data

react_on = "$"
client = discord.Client()
csv_writer_lock = threading.Lock()
csvfile = open('msgs.csv', 'a', newline='')
msgwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

@client.event
async def on_ready():
    print(f"Hellowo, mwy nwame is {client.user}")


def timeout_user(*, user_id: int, guild_id: int, until: int):
    endpoint = f'guilds/{guild_id}/members/{user_id}'
    headers = {"Authorization": f"Bot {TOKEN}"}
    url = BASE + endpoint
    timeout = (datetime.datetime.utcnow() + datetime.timedelta(minutes=until)).isoformat()
    json = {'communication_disabled_until': timeout}
    session = requests.patch(url, json=json, headers=headers)
    if session.status_code in range(200, 299):
        return session.json()
    else:
        return print("Did not find any\n", session.status_code)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.author.id == -1:
        print("trying to timeout uwu")
        await timeout_user(user_id=message.author.id, guild_id=message.guild.id, until=1)
    if message.content == f"{react_on}hello":
        rep = "Hello"
        if random.randint(0, 10) > 5:
            rep += " handsome!"
        else:
            rep += "!"
        await message.channel.send(rep)
    elif message.content.startswith(f"{react_on}bottom"):
        bottomify = message.content.split(f'{react_on}bottom', 1)[1]
        uwu = subprocess.run(["./bottomify", "-b", bottomify], capture_output=True)
        await message.channel.send(uwu.stdout.decode("utf8"))
    elif message.content == f"{react_on}help":
        rep = """```K-Konichiwa!
$help - showws thwis mwessage 
$rate <msg> - telwlws you how owo-kawai <msg> is - scowre >= 1 is owo :3
$owofy <msg> - owofy <msg> nyaa~~
$owo - OwO```"""
        await message.channel.send(rep)
    elif message.content.startswith(f"{react_on}love"):
        user = message.mentions[0]
        for i in range(0, random.randint(5, 25)):
            time.sleep(1)
            await user.send('👀')
    elif message.content == f"{react_on}pengu":
        t = ""
        while len(t) < 10:
            normal = subprocess.run(["./random_pengu.sh", ""], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    check=True, text=True)
            t = normal.stdout
        await message.channel.send(t)
    elif message.content == f"{react_on}owo":
        await message.channel.send(random.choice(uwu_data.int_emote))
    elif message.content.startswith(f"{react_on}owofy "):
        answer = f"{owo.owofy(message.content.split(f'{react_on}owofy', 1)[1])}"
        await message.channel.send(f'```{answer.replace("`", "")} ```')
    elif message.content.startswith(f"{react_on}rate "):
        score = owo.score(message.content.split(f'{react_on}rate', 1)[1])
        await message.channel.send(f'S-Senpai ywou scwored a {score:.2f}')
    else:
        words = message.content.split()
        nmsg = ""
        for word in words:
            if not word.startswith("http") and not(word[0] == "<" and word[-1] == ">"):
                nmsg += f"{word} "
        msg = nmsg
        owo_score = owo.score(msg)
        print(owo_score)
        is_only_alpha = True
        for ltr in msg:
            if ltr.isalpha():
                is_only_alpha = False
        if owo_score < 1 and not is_only_alpha and message.channel.id == 937306121901850684:
            answer = owo.owofy(msg)
            answer_score = owo.score(answer)
            print(answer_score)
            await message.channel.send(
                    f'{random.choice(uwu_data.sowwy)} <@{message.author.id}> youw seem to nwot hav owofied ywour text.. h-here lwet me show you:\n```{answer.replace("`", "")} ```')
    print(message.author.id)
    with csv_writer_lock:
        msgwriter.writerow([message.author.id, message.channel.id, time.time(), message.content])
        csvfile.flush()

BASE = "https://discord.com/api/v9/"
TOKEN = open("token.owo", "r").read()
client.run(TOKEN)
