import discord
import json

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


@client.event
async def on_ready():
    print('----------------')
    print('secRet bot ready')
    print('----------------')


@client.event
async def on_member_join(member):
    print('--> ' + member.nick + ' has joined.')


@client.event
async def on_member_remove(member):
    print('--> ' + member.nick + ' has joined.')


@client.event
async def on_message(message):
    await message_handler.on_message(message)


# initialize discord bot
client.run(configs['discord_token'])
