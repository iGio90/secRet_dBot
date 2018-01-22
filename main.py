import asyncio
import discord
import json
import threading

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

# event bus and loop
main_loop = asyncio.get_event_loop()
bus = EventBus()

# secret thread for additional periodic stuffs
secret = SecRet(bus)
secret.setName('secRet')
secret.start()


@bus.on('secret_send')
def secret_send(message=None):
    """
    can be used from other threads :P

    :param: message
    a string or embed object
    """
    main_loop.create_task(_as_secret_send(message))


async def _as_secret_send(message):
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
