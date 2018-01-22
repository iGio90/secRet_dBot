import asyncio
import discord
import json
import os
import sys

from event_bus import EventBus
from github import Github
from message_handler import MessageHandler
from mongoengine import *
from secret import SecRet

# read configs
with open('configs.json', 'r') as f:
    configs = json.load(f)

# event bus and loop
main_loop = asyncio.get_event_loop()
bus = EventBus()

# mongo db free4all
connect('secret')
mongo_db = Document._get_db()

# discord
discord_client = discord.Client()
secret_server = discord.Server(id='326095959173890059')
secret_channel = discord.Channel(id='404630967257530372',
                                 server=secret_server)
welcome_channel = discord.Channel(id='404795628019777557',
                                  server=secret_server)

# github
g = Github(configs['github_username'], configs['github_password'])
repo = g.get_repo('iGio90/secRet_dBot')

# message handler
message_handler = MessageHandler(bus, discord_client, mongo_db, secret_server, secret_channel, repo)

# secret thread for additional periodic stuffs
secret = SecRet(bus, repo)
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


@bus.on('secret_restart')
def secret_restart():
    """
    restart the bot with updated code
    """
    main_loop.create_task(_restart())


@bus.on('secret_ping')
def secret_ping():
    """
    hourly ping from secret parallel thread
    """
    message_handler.status(None)


@discord_client.event
async def on_ready():
    print('----------------')
    print('secRet bot ready')
    print('----------------')


@discord_client.event
async def on_member_join(member):
    await discord_client.send_message(welcome_channel, '**[*]** ' + member.mention + ' has joined!')


@discord_client.event
async def on_member_remove(member):
    await discord_client.send_message(welcome_channel, '**[*]** ' + member.mention + ' has left!')


@discord_client.event
async def on_message(message):
    await message_handler.on_message(message)


async def _restart():
    await discord_client.send_message(secret_channel, '**[*]** restarting secRet')
    os.execv(sys.executable, [sys.executable.split("/")[-1]] + sys.argv)


async def _as_secret_send(message):
    if message:
        if isinstance(message, str):
            await discord_client.send_message(secret_channel, message)
        elif isinstance(message, discord.Embed):
            await discord_client.send_message(secret_channel, embed=message)


# initialize discord bot
discord_client.run(configs['discord_token'])
