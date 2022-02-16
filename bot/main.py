#! /bin/python3
import asyncio
import csv
import datetime
import os
import random
import subprocess
import sys
import threading
import time
import discord
import requests
from discord.ext import commands
import owolib
import uwu_data
import catapi

react_on = "$"
client = discord.Client()
csv_writer_lock = threading.Lock()
q_writer_lock = threading.Lock()

tries = 0
bpath = f"{sys.argv[1]}/"

csvfile = open(bpath + 'msgs.csv', 'a', newline='')
msgwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

gen_res = open(bpath + 'gen_text.txt')
gens = gen_res.read().split("====================")

BASE = "https://discord.com/api/v9/"
TOKEN = open(bpath + "token.owo", "r").read()
desc = "Pwease end my misewy, nyaaa~"
bot = commands.Bot(command_prefix=react_on, description=desc)

catapi_key = open(bpath + "cat_token.owo", "r").read()
catapi = catapi.CatApi(api_key=catapi_key)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


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


def genRow(maxlen: int, curRow: int):
    ltr = chr(ord('A') + curRow)
    opad = maxlen - curRow - 1
    if (curRow == 0):
        return f"{'.' * opad}{ltr}{'.' * opad}"
    return f"{'.' * opad}{ltr}{'.' * ((curRow * 2) - 1)}{ltr}{'.' * opad}"


@bot.command()
async def diamond(ctx, nrows: int):
    if nrows > 22:
        await ctx.send(f"{random.choice(uwu_data.sowwy)}, thiws is too mwuch fow me to take nyaaa~")
        return
    elif nrows < 1:
        await ctx.send(f"{random.choice(uwu_data.sowwy)}, thiws is nwot enough fow me to take nyaaa~")
        return
    else:
        result = []
        for i in range(0, nrows - 1):
            result.append(genRow(nrows, i))
        for i in range(nrows - 1, -1, -1):
            result.append(genRow(nrows, i))
        d = '\n'.join(result)
        await ctx.send(f"```\n{d}\n```")


@bot.command()
async def obamamedal(ctx):
    await ctx.send("https://media.discordapp.net/attachments/798609300955594782/816701722818117692/obama.jpg")


@bot.command()
async def owobaamamedal(ctx):
    await ctx.send("https://cdn.discordapp.com/attachments/938102328282722345/939605208999264367/Unbenannt.png")


@bot.command()
async def crash():
    sys.exit(0)


@bot.command()
async def redeploy(ctx):
    os.chdir(bpath)
    uwu = subprocess.run(["git", "pull"], capture_output=True)
    await ctx.send(f"```\n{uwu}\n```")
    sys.exit(0)


@bot.command()
async def hello(ctx):
    await ctx.send(random.choice(["Hello", "Hello handsome :)"]))


@bot.command()
async def generate(ctx):
    resp = gens.pop()
    await ctx.send(resp.replace("everyone", "evwyone").replace("here", "hewe"))


@bot.command()
async def bottom(ctx, msg: str):
    bottom = subprocess.run([bpath + "bottomify", "-b", msg], capture_output=True)
    await ctx.send(bottom.stdout.decode("utf8"))


@bot.command()
async def unbottom(ctx, msg: str):
    uwu = subprocess.run([bpath + "bottomify", "-r", msg], capture_output=True)
    await ctx.send(uwu.stdout.decode("utf8"))


@bot.command()
async def love(ctx, msg: str):
    user = ctx.message.mentions[0]
    for i in range(0, random.randint(5, 25)):
        time.sleep(1)
        await user.send('👀')


@bot.command(brief="OwO")
async def owo(ctx):
    await ctx.send(random.choice(uwu_data.int_emote))

@bot.command(brief="lena")
async def baaa(ctx):
    await ctx.send("<@898152253330972672>")
    await ctx.send("https://cdn.discordapp.com/attachments/779413828051664966/943597938687508500/unknown.png")
    
@bot.command(brief="cat")
async def aww(ctx):
    task = loop.create_task(catapi.search_images(limit=1))
    await task
    await ctx.send(task.result()[0].url)


@bot.command(brief="owofy <msg> nyaa~~")
async def owofy(ctx, *, msg: str):
    owofied = owolib.owofy(msg)
    await ctx.send(f'```{owofied.replace("`", "")} ```')


@bot.command(brief="telwlws you how owo-kawai <msg> is - scowre >= 1 is owo :3")
async def rate(ctx, msg: str):
    score = owolib.score(msg)
    await ctx.send(f'S-Senpai ywou scwored a {score:.2f}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.author.id == -1:
        print("trying to timeout uwu")
        await timeout_user(user_id=message.author.id, guild_id=message.guild.id, until=1)
    if message.channel.id == 937306121901850684:
        words = message.content.split()
        nmsg = ""
        for word in words:
            if not word.startswith("http") and not (word[0] == "<" and word[-1] == ">"):
                nmsg += f"{word} "
        msg = nmsg
        owo_score = owolib.score(msg)
        print(owo_score)
        is_only_alpha = True
        for ltr in msg:
            if ltr.isalpha():
                is_only_alpha = False
        if owo_score < 1 and not is_only_alpha:
            answer = owolib.owofy(msg)
            answer_score = owolib.score(answer)
            print(answer_score)
            await message.channel.send(
                f'{random.choice(uwu_data.sowwy)} <@{message.author.id}> youw seem to nwot hav owofied ywour text.. h-here lwet me show you:\n```{answer.replace("`", "")} ```')
    with csv_writer_lock:
        msgwriter.writerow([message.author.id, message.channel.id, time.time(), message.content])
    csvfile.flush()


loop = asyncio.get_event_loop()
loop.create_task(bot.start(TOKEN))
loop.create_task(client.start(TOKEN))
loop.run_forever()
