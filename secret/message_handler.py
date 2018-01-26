import json
import random

import discord
import urllib
from secret import utils

from secret.api import gplay, wikipedia, accuweather
from secret.discord_commands import command_test, commands_git, commands_gif, command_help, command_status
from mongo_models import command_log


class MessageHandler(object):
    """
    handle messages from discord #secRet channel.
    code here your stuffs keeping the following flow:
    1) add the command to the map (always follow alphabetical order)
    2) add the function handler to this class, which must be async
    3) **OPTIONAL** check other functions to have a very quick understanding
    4) if it's too much code, consider create your own class/scripts inside commands package
       and feed it with client, bus and whatever is needed

    :param: secret_context
    our context holding all the references and things we can use
    """

    def __init__(self, secret_context):
        # load maps
        with open('secret/discord_commands/map/admin_commands.json', 'r') as f:
            self.admin_commands_map = json.load(f)
        with open('secret/discord_commands/map/dev_commands.json', 'r') as f:
            self.dev_commands_map = json.load(f)
        with open('secret/discord_commands/map/user_commands.json', 'r') as f:
            self.commands_map = json.load(f)
        with open('secret/discord_commands/map/shortcuts.json', 'r') as f:
            self.shortcuts_map = json.load(f)

        # hold the last command used
        self.last_command = {}
        # secret context
        self.secret_context = secret_context
        # google play api
        self.gplay_handler = gplay.GPlay()

        # arbitrary py execution for command testing
        self.cmd_tester = command_test.TestCMD(self.secret_context)

    ##
    # commands
    ##

    async def commands(self, message):
        """
        list the commands
        """
        await command_help.commands(message, self.secret_context.discord_client, self.admin_commands_map,
                                    self.dev_commands_map, self.commands_map, self.shortcuts_map)

    async def commands_history(self, message):
        cmd_list = message.content.split(" ")
        if len(cmd_list) == 1:
            embed = utils.build_default_embed('commands history', '-', discord.Color.teal(), icon=False)
            for log in command_log.CommandLog.objects[:10]:
                embed.add_field(name=log.user_name, value=log.command, inline=False)
            await self.secret_context.discord_client.send_message(message.channel, embed=embed)
        else:
            if cmd_list[1] == 'clear':
                c = command_log.CommandLog.objects.count()
                command_log.CommandLog.drop_collection()
                await self.secret_context.discord_client.send_message(
                    message.channel, embed=utils.simple_embed('done', "removed " + str(c) + " entries",
                                                              discord.Color.dark_green()))

    async def core_update(self, message):
        parts = message.content.split[" "]
        if len(parts) > 2:
            if parts[1] == 'core':
                self.secret_context.bus.emit('secret_update', print_no_update=True)
            elif parts[2] == 'web':
                self.secret_context.bus.emit('secret_update', print_no_update=True, web_update=True)
        else:
            self.secret_context.bus.emit('secret_update', print_no_update=True)

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
            await self.secret_context.discord_client.send_message(message.channel, embed=embed)

    async def exec(self, message):
        cmd = message.content.replace("!exec ", "")
        r = utils.run_shell_command(cmd)
        for line in r:
            await self.secret_context.discord_client.send_message(message.channel, line)

    async def gif(self, message):
        await commands_gif.on_message(message, self.secret_context)

    async def git(self, message):
        await commands_git.git(message, self.secret_context)

    async def gplay(self, message):
        await self.gplay_handler.on_message(message, self.secret_context)

    async def help(self, message):
        """
        print help
        """
        await command_help.help(message, self.secret_context.discord_client, [
            self.admin_commands_map, self.dev_commands_map, self.commands_map
        ], self.shortcuts_map)

    async def pr(self, message):
        await commands_git.pr(message, self.secret_context)

    async def qr_generate(self, message):
        embed = discord.Embed(title='QR Code generator', type='rich',
                              color=discord.Colour.green())
        message_data = message.content[4:]
        data = urllib.parse.quote_plus(message_data)
        if data is "":
            embed.add_field(name="Error", value="Please man, give me some data!", inline=False)
        else:
            if len(message_data) > 300:
                embed.add_field(name="Error", value="Data must be < 300 char", inline=False)
            else:
                embed.set_image(url="https://api.qrserver.com/v1/create-qr-code/?data=" + data + "&size=200x200")

        await self.secret_context.discord_client.send_message(message.channel, embed=embed)

    async def repeat(self, message):
        if 'function' in self.last_command and 'message' in self.last_command:
            if message.author.id == self.last_command['message'].author.id:
                await self.last_command['function'](self.last_command['message'])

    async def restart(self, message):
        """
        restart the scripts (update changes)
        """
        self.secret_context.bus.emit('secret_restart')

    async def roll(self, message):
        """
        simple roll accepting max as first arg
        """
        parts = message.content.split(" ")
        max = 100
        if len(parts) > 1:
            try:
                max = int(parts[1])
            except Exception as e:
                pass

        embed = utils.simple_embed('roll', '**' + str(random.randint(0, max)) + '**', utils.random_color())
        await self.secret_context.discord_client.send_message(message.channel, embed=embed)

    async def rules(self, message):
        """
        print rules
        """
        embed = utils.build_default_embed('', '', discord.Color.dark_green())
        s = open('RULES.md', 'r')
        msg = s.read()
        embed.add_field(name="Rules of the house", value=msg, inline=False)
        await self.secret_context.discord_client.send_message(message.channel, embed=embed)

    async def status(self, message):
        if message:
            parts = message.content.split(" ")
            if len(parts) < 2:
                # print the help
                self.secret_context.bus.emit('secret_command', command='!help status')
            else:
                if parts[1] == 'bot':
                    await command_status.bot_status(self.secret_context)
                elif parts[1] == 'discord':
                    await command_status.discord_status(self.secret_context)
                elif parts[1] == 'git':
                    await command_status.git_status(self.secret_context)
                elif parts[1] == 'mongo':
                    await command_status.mongo_status(self.secret_context)
                elif parts[1] == 'all':
                    await  command_status.secret_status(self.secret_context)
        else:
            await command_status.bot_status(self.secret_context)

    async def test_command(self, message, lang):
        await self.cmd_tester.on_message(message, lang)

    async def weather(self, message):
        await accuweather.on_message(message, self.secret_context)

    async def wikipedia(self, message):
        await wikipedia.on_message(message, self.secret_context)

    ##
    # end commands
    ##

    async def on_message(self, message):
        """
        don't touch this! keep it abstract
        """

        # we don't want interaction in any other channels
        if message.channel.id != self.secret_context.secret_channel.id:
            return

        # quick content reference
        content = message.content

        # command test
        if content.startswith("```") and \
                (utils.is_dev(message.author) or utils.is_admin(message.author)):
            parts = content.split('\n')
            lang = parts[0].replace("```", '')
            if lang in self.cmd_tester.supported_languages:
                await self.test_command(message, lang)
            return

        # we also want to skip anything that doesn't start with the prefix
        if not content.startswith("!"):
            return

        # strip prefix
        content = content[1:]

        # get base command
        base_command = content.split(" ")

        # the function to call
        cmd_funct = None

        # check if it's a shortcut
        if base_command[0] in self.shortcuts_map:
            base_command[0] = self.shortcuts_map[base_command[0]]

        if base_command[0] in self.commands_map:
            # user commands
            cmd_funct = self._get_command_function(self.commands_map, base_command)
        elif base_command[0] in self.dev_commands_map and utils.is_dev(message.author):
            # dev commands
            cmd_funct = self._get_command_function(self.dev_commands_map, base_command)
        elif base_command[0] in self.admin_commands_map and utils.is_admin(message.author):
            # admin commands
            cmd_funct = self._get_command_function(self.admin_commands_map, base_command)

        if cmd_funct is not None:
            # store last command function for repeat
            if base_command[0] != '!':
                self.last_command['function'] = cmd_funct
                self.last_command['message'] = message

            # log command issued on mongo. check if author is there
            # since we can come from the event bus which build the
            # msg object in runtime
            if message.author is not None:
                cmd_log = command_log.CommandLog(user_name=message.author.name,
                                                 user_id=message.author.id,
                                                 command=content)
                cmd_log.save()

            await cmd_funct(message)

    def _get_command_function(self, map, base_command):
        command = map[base_command[0]]
        return getattr(self, command["function"])
