import asyncio
import discord
import os
import sys
import utils


from commands import commands_git

# commands map for help
commands_map = {
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

    :param: bus
    event bus
    :param: client
    the discord client
    :param: secret_server
    instance of discord server object holding server id
    :param: secret_channel
    instance of discord channel object holdin #secRet id
    :param: git_repo
    the git repository
    """

    def __init__(self, bus, client, secret_server, secret_channel, git_repo):
        self.bus = bus
        self.client = client
        self.secret_server = secret_server
        self.secret_channel = secret_channel
        self.git_repo = git_repo

    async def cleanup(self, message):
        """
        clean the whole channel. delete all messages
        """
        c = len(await self.client.purge_from(message.channel, limit=100000))
        await self.client.send_message(message.channel, '**[*]** ' + str(c) + ' message deleted!')

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

    async def devme(self, message):
        s = open('DOCUMENTATION.md', 'r')
        msg = s.read()
        l = 0
        msg_len = len(msg)
        # message is too long :S
        while l <= msg_len:
            try:
                m = msg[l:l + 1000]
            except Exception as e:
                m = msg_len[l:msg_len - 1]
            l += 1000
            embed = utils.build_default_embed('', '', discord.Color.dark_green())
            embed.add_field(name="contribute and improve secRet dBot", value=m, inline=False)
            await self.client.send_message(message.channel, embed=embed)

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
        self.bus.emit('secret_restart')

    async def rules(self, message):
        embed = utils.build_default_embed('', '', discord.Color.dark_green())
        s = open('RULES.md', 'r')
        msg = s.read()
        embed.add_field(name="Rules of the house", value=msg, inline=False)
        await self.client.send_message(message.channel, embed=embed)

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

        # parse base commands (not mapped)
        if content == 'commands':
            await self.commands(message)
        elif content == 'rules':
            await self.rules(message)
        elif content == 'devme':
            await self.devme(message)
        # parse user commands
        elif content in commands_map:
            command = commands_map[content]
            command_function = getattr(self, command["function"])
            await command_function(message)
        # check and parse admin commands
        elif utils.is_admin(message.author):
            if content in admin_commands_map:
                command = admin_commands_map[content]
                command_function = getattr(self, command["function"])
                await command_function(message)
