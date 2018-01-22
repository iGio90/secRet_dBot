import asyncio
import discord
import os
import sys


class MessageHandler(object):
    """
    handle messages from discord #secRet channel

    :param client
    the discord client
    :param secret_server
    instance of discord server object holding server id
    :param secret_channel
    instance of discord channel object holdin #secRet id
    :param git_repo
    the git repository
    """

    def __init__(self, client, secret_server, secret_channel, git_repo):
        self.client = client
        self.secret_server = secret_server
        self.secret_channel = secret_channel
        self.git_repo = git_repo

    def is_admin(self, id):
        """
        :param id
        the id to check

        :return:
        true for admins
        """
        return id in [
            '168018245943558144'
        ]

    def get_commits(self):
        """
        :return:
        an embed discord object with the latest 10 commits
        """
        embed = discord.Embed(title='secRet', type='rich', description='Last 10 commits',
                              color=discord.Colour.dark_purple())
        embed.set_thumbnail(url="https://octodex.github.com/images/heisencat.png")
        embed.set_author(name="iGio90/secRet-dBot", url="https://github.com/iGio90/secRet_dBot",
                         icon_url="http://paulcilwa.com/Content/Science/Science.png")
        k = 0
        for commit in self.git_repo.get_commits():
            if k == 10:
                break
            embed.add_field(name=commit.commit.message, value=commit.commit.author.name, inline=False)
            k += 1
        return embed

    @asyncio.coroutine
    async def on_message(self, message):

        # we don't want interaction in any other channels
        if message.channel.id != self.secret_channel.id:
            return

        # switch user messages
        if message.content.startswith("!commits"):
            await self.client.send_message(message.channel, embed=self.get_commits())

        # switch admin messages
        if not self.is_admin(message.author.id):
            return

        if message.content.startswith("!restart"):
            await self.client.send_message(message.channel, "[*] restarting secRet")
            os.execv(sys.executable, [sys.executable.split("/")[-1]] + sys.argv)
        elif message.content.startswith("!cleanup"):
            await self.client.send_message(message.channel, '[*] cleaning!')
            await self.client.purge_from(message.channel)
