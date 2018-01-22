import asyncio
import discord
import json
import threading
import time

from datetime import datetime
from event_bus import EventBus
from github import Github
from message_handler import MessageHandler
from secret import SecRet

# read configs
with open('configs.json', 'r') as f:
    configs = json.load(f)

# discord
client = discord.Client()
secret_server = discord.Server(id='326095959173890059')
secret_channel = discord.Channel(id='404630967257530372',
                                 server=secret_server)
welcome_channel = discord.Channel(id='404795628019777557',
                                  server=secret_server)

# github
g = Github(configs['github_username'], configs['github_password'])
repo = g.get_repo('iGio90/secRet_dBot')

# message handler
message_handler = MessageHandler(client, secret_server, secret_channel, repo)

# secret thread for additional periodic stuffs
secret = SecRet()
secret.setName('secRet')
secret.start()

# event bus
bus = EventBus()


def ding():
    now = datetime.now()
    s = ''
    for i in range(0, now.minute):
        s += 'DING '
    bus.emit('secret_send', message=s)


@asyncio.coroutine
@bus.on('secret_send')
async def secret_send(message=None):
    print("secret_send called")
    print("message: " + message)
    """
    can be used from other threads :P

    :param: message
    a string or embed object
    """
    if message:
        if isinstance(message, str):
            await client.send_message(secret_channel, message)
        elif isinstance(message, discord.Embed):
            await client.send_message(secret_channel, embed=message)


@client.event
async def on_ready():
    print('----------------')
    print('secRet bot ready')
    print('----------------')

    # DING
    now = datetime.now()
    c_min = now.minute
    c_sec = now.second
    l_min = 59 - c_min
    l_sec = 59 - c_sec + (60 * l_min)
    threading.Timer(l_sec, ding).start()


@client.event
async def on_member_join(member):
    await client.send_message(welcome_channel, '[*] ' + member.mention() + ' has joined!')


@client.event
async def on_member_remove(member):
    await client.send_message(welcome_channel, '[*] ' + member.mention() + ' has left!')


@client.event
async def on_message(message):
    await message_handler.on_message(message)


# initialize discord bot
client.run(configs['discord_token'])
