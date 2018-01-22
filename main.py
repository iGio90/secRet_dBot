import asyncio
import discord
import json

import time
from github import Github
from threading import Thread

client = discord.Client()
configs = None


class SecRet(Thread):
    def __init__(self, git_user, git_pass):
        Thread.__init__(self)

        # setup github
        self.g = Github(git_user, git_pass)
        self.repo = self.g.get_repo('iGio90/secRet_dBot')

    def run(self):
        while True:
            pulls = self.repo.get_pulls
            print(pulls)
            time.sleep(60 * 15)


@client.event
async def on_ready():
    print('----------------')
    print('secRet bot ready')
    print(client.user.name)
    print(client.user.id)
    print('----------------')


@client.event
async def on_message(message):
    if message.channel.name != "secret":
        # we don't want interaction in any other channels
        return

    print(message.content)

    if message.content.startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1
        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')


def main():
    # read configs
    with open('configs.json', 'r') as f:
        configs = json.load(f)

    secret = SecRet(configs['github_username'], configs['github_password'])
    secret.setName('secRet')
    secret.start()

    # setup discord bot
    client.run(configs['discord_token'])


if __name__ == '__main__':
    main()
