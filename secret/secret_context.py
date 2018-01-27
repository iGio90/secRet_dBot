import asyncio
import discord

from event_bus import EventBus
from github import Github
from secret.message_handler import MessageHandler
from secret.handlers import status
from mongoengine import *


class SecRetContext(object):
    def __init__(self, configs):
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
        self.git_client = Github(configs['github_username'], configs['github_password'])
        self.git_repo = self.git_client.get_repo('secRetDBot/secRet_dBot')
        self.web_repo = self.git_client.get_repo('secRetDBot/secRet-bot-frontend')

        # discord message handler
        self.message_handler = MessageHandler(self)

        # handlers
        self.handler_status = status.Status(self)

    @staticmethod
    def api_keys():
        return {
            'csys_app_id': '73ca4c15-959f-4bd4-8bb7-233b2c306b0a',
            'csys_sec': 'WVmO23xfzMbumtgXCp7MQAFTeBCohNZx'
        }
