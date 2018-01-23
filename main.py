import asyncio
import discord
import json
import os
import sys
import utils

from event_bus import EventBus
from github import Github
from message_handler import MessageHandler
from mongoengine import *
from secret import SecRet


class SecRetDBot(object):
    def __init__(self):
        # read configs
        with open('configs.json', 'r') as f:
            self.configs = json.load(f)

        # event bus and loop
        self.main_loop = asyncio.get_event_loop()
        self.bus = EventBus()

        # mongo db free4all
        connect('secret')
        self.mongo_db = Document._get_db()

        # discord
        self.discord_client = discord.Client()
        self.secret_server = discord.Server(id='326095959173890059')
        self.secret_channel = discord.Channel(id='404630967257530372',
                                              server=self.secret_server)
        self.welcome_channel = discord.Channel(id='404795628019777557',
                                               server=self.secret_server)

        # github
        self.git_client = Github(self.configs['github_username'], self.configs['github_password'])
        self.repo = self.git_client.get_repo('secRetDBot/secRet_dBot')

        # message handler
        self.message_handler = MessageHandler(self.bus, self.discord_client, self.mongo_db,
                                              self.secret_server, self.secret_channel,
                                              self.git_client, self.repo)

        # secret thread for additional periodic stuffs
        secret = SecRet(self.bus, self.repo)
        secret.setName('secRet')
        secret.start()

        # register bus events
        self.bus.add_event(self.secret_send, 'secret_send')
        self.bus.add_event(self.secret_restart, 'secret_restart')
        self.bus.add_event(self.secret_ping, 'secret_ping')
        self.bus.add_event(self.secret_command, 'secret_command')

        # register discord events
        self.discord_client.event(self.on_ready)
        self.discord_client.event(self.on_member_join)
        self.discord_client.event(self.on_member_remove)
        self.discord_client.event(self.on_message)

    async def on_ready(self):
        print('----------------------------')
        print('secRet bot connected')
        print('----------------------------')

    async def on_member_join(self, member):
        await self.discord_client.send_message(self.welcome_channel, '**[*]** ' + member.mention + ' has joined!')

    async def on_member_remove(self, member):
        await self.discord_client.send_message(self.welcome_channel, '**[*]** ' + member.mention + ' has left!')

    async def on_message(self, message):
        await self.message_handler.on_message(message)

    def secret_command(self, command):
        """
        allow to quickly send a command using bus.
        a short usage case for this:
        somewhere inside your new function script you want to handle an error
        by simply printing the help of the command.
        as we are sending it from discord, we can use the bus to send a "!help *function_name"
        with bus
        """
        message = discord.Message()
        message.channel = self.secret_channel
        message.server = self.secret_server
        message.content = command
        self.main_loop.create_task(self.message_handler.secret_status(None))

    def secret_ping(self):
        """
        hourly ping from secret parallel thread
        """
        self.main_loop.create_task(self.message_handler.secret_status(None))

    def secret_restart(self):
        """
        restart the bot with updated code
        """
        self.main_loop.create_task(self._restart())

    def secret_send(self, message=None):
        """
        can be used from other threads :P

        :param: message
        a string or embed object
        """
        self.main_loop.create_task(self._as_secret_send(message))

    def start(self):
        """
        connect the discord bot
        """
        self.discord_client.run(self.configs['discord_token'])

    async def _as_secret_send(self, message):
        if message:
            if isinstance(message, str):
                await self.discord_client.send_message(self.secret_channel, message)
            elif isinstance(message, discord.Embed):
                await self.discord_client.send_message(self.secret_channel, embed=message)

    async def _restart(self):
        print('----------------------------')
        print('secRet bot is now restarting')
        print('----------------------------')
        await self.discord_client.send_message(self.secret_channel,
                                               embed=utils.simple_embed('restart', 'restarting secRet dBot',
                                                                        utils.random_color()))
        os.execv(sys.executable, [sys.executable.split("/")[-1]] + sys.argv)


def main():
    sdb = SecRetDBot()
    sdb.start()


if __name__ == "__main__":
    main()
