import asyncio
import os
import sys

import discord

import utils

from commands import commands_git

# commands map for help
commands_map = {
    "commands": {
        "author": "iGio90",
        "description": "commands list",
        "function": "commands"
    },
    "commits": {
        "author": "iGio90",
        "description": "last 10 commits on secRet repo",
        "function": "commits"
    },
    "help": {
        "author": "iGio90",
        "description": "initial help",
        "function": "help"
    },
}

admin_commands_map = {
    "cleanup": {
        "author": "iGio90",
        "description": "cleanup the channel.",
        "function": "cleanup"
    },
    "restart": {
        "author": "iGio90",
        "description": "restart secRet. flush scripts",
        "function": "restart"
    }
}


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

    async def cleanup(self, message):
        """
        clean the whole channel. delete all messages
        """
        c = len(await self.client.purge_from(message.channel))
        await self.client.send_message(message.channel, '[*] ' + str(c) + ' message deleted!')

    async def commands(self, message):
        """
        list the commands from both the maps
        """
        # user commands
        embed = utils.build_default_embed('', '', discord.Color.gold())
        embed.add_field(name="user commands", value='-', inline=False)
        for cmd_name, cmd in commands_map.items():
            description = ''
            if 'description' in cmd:
                description = cmd['description']
            embed.add_field(name="!" + cmd_name, value=description, inline=False)
        await self.client.send_message(message.channel, embed=embed)

        # admin commands
        embed = utils.build_default_embed('', '', discord.Color.teal())
        embed.add_field(name="admin commands", value='-', inline=False)
        for cmd_name, cmd in admin_commands_map.items():
            description = ''
            if 'description' in cmd:
                description = cmd['description']
            embed.add_field(name="!" + cmd_name, value=description, inline=False)
        await self.client.send_message(message.channel, embed=embed)

    async def commits(self, message):
        """
        list last 10 commits in the repo
        """
        commits_embed = commands_git.build_commit_list_embed(self.git_repo)
        await self.client.send_message(message.channel, embed=commits_embed)

    async def help(self, message):
        """
        print help
        """
        embed = discord.Embed(title='', type='rich',
                              description="\ngoal is to build me as an automated **bot** with whatever feature "
                                          "people would like to code. I'll soon run on a virtual"
                                          " machine with **root** privileges,"
                                          "but meanwhile, I can already do something:\n\n",
                              color=discord.Colour.dark_red())
        embed.set_thumbnail(url="http://paulcilwa.com/Content/Science/Science.png")
        embed.set_author(name="secRet", url="https://secret.re")
        embed.add_field(name="!commands", value="something to interact with me", inline=False)
        embed.add_field(name="!devme", value="info and help about coding features", inline=False)
        embed.add_field(name="!rules", value="a world without rules... mhhh chaos", inline=False)
        await self.client.send_message(message.channel, embed=embed)

    async def restart(self, message):
        """
        restart the scripts (update changes)
        """
        await self.client.send_message(message.channel, "[*] restarting secRet")
        os.execv(sys.executable, [sys.executable.split("/")[-1]] + sys.argv)

    @asyncio.coroutine
    async def on_message(self, message):
        """
        don't touch this! keep it abstract
        """

        # we don't want interaction in any other channels
        if message.channel.id != self.secret_channel.id:
            return

        # quick content reference
        content = message.content

        # we also want to skip anything that doesn't start with the prefix
        if not content.startswith("!"):
            return

        # strip prefix
        content = content[1:]

        # parse user commands
        if content in commands_map:
            command = commands_map[content]
            command_function = getattr(self, command["function"])
            await command_function(message)

        # check and parse admin commands
        if utils.is_admin(message.author.id):
            if content in admin_commands_map:
                command = admin_commands_map[content]
                command_function = getattr(self, command["function"])
                await command_function(message)
