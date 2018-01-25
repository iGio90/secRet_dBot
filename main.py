import discord
import json
import os
import sys

from secret import secret_context, secret_rest, secret_worker, utils


class SecRetDBot(object):
    def __init__(self):
        # read configs
        with open('configs.json', 'r') as f:
            self.configs = json.load(f)

        # context which hold a ref of everything we can use all-around
        self.secret_context = secret_context.SecRetContext(self.configs)

        # register bus events
        self.secret_context.bus.add_event(self.secret_send, 'secret_send')
        self.secret_context.bus.add_event(self.secret_restart, 'secret_restart')
        self.secret_context.bus.add_event(self.secret_ping, 'secret_ping')
        self.secret_context.bus.add_event(self.secret_command, 'secret_command')

        # register discord events
        self.secret_context.discord_client.event(self.on_ready)
        self.secret_context.discord_client.event(self.on_member_join)
        self.secret_context.discord_client.event(self.on_member_remove)
        self.secret_context.discord_client.event(self.on_message)

    async def on_ready(self):
        print('----------------------------')
        print('secRet bot connected')
        print('----------------------------')
        embed = utils.simple_embed('secRet dBot', 'services initialized',
                                   utils.random_color())
        embed.set_author(name='secret', url='http://secret.re', icon_url=utils.ICON)
        embed.set_thumbnail(url=utils.ICON)
        embed.add_field(name="!help", value="initial help")
        embed.add_field(name="!commands", value="available commands")
        await self.secret_context.discord_client.send_message(self.secret_context.secret_channel, embed=embed)

    async def on_member_join(self, member):
        embed = utils.simple_embed('Welcome', member.mention + ' has join',
                                   utils.random_color())
        await self.secret_context.discord_client.send_message(
            self.secret_context.welcome_channel, embed=embed)

    async def on_member_remove(self, member):
        embed = utils.simple_embed('Welcome', member.mention + ' has left',
                                   utils.random_color())
        await self.secret_context.discord_client.send_message(self.secret_context.welcome_channel, embed=embed)

    async def on_message(self, message):
        await self.secret_context.message_handler.on_message(message)

    def secret_command(self, command):
        """
        allow to quickly send a command using bus.
        a short usage case for this:
        somewhere inside your new function script you want to handle an error
        by simply printing the help of the command.
        as we are sending it from discord, we can use the bus to send a "!help *function_name"
        with bus
        """
        message = discord.Message(reactions=[])
        message.channel = self.secret_context.secret_channel
        message.server = self.secret_context.secret_server
        message.content = command
        # kill the author
        message.author = None
        self.secret_context.main_loop.create_task(
            self.secret_context.message_handler.on_message(message))

    def secret_ping(self):
        """
        hourly ping from secret parallel thread
        """
        self.secret_context.main_loop.create_task(
            self.secret_context.message_handler.secret_status(None))

    def secret_restart(self):
        """
        restart the bot with updated code
        """
        self.secret_context.main_loop.create_task(self._restart())

    def secret_send(self, message=None):
        """
        can be used from other threads :P

        :param: message
        a string or embed object
        """
        self.secret_context.main_loop.create_task(self._as_secret_send(message))

    def start(self):
        """
        setup rest server, secret worker and discord bot
        """
        try:
            # rest server
            rest = secret_rest.SecRetRest(self.secret_context)
            rest.start()

            # secret thread for additional periodic stuffs
            secret_worker_thread = secret_worker.SecRet(self.secret_context)
            secret_worker_thread.setName('secRet worker')
            secret_worker_thread.start()

            self.secret_context.discord_client.run(self.configs['discord_token'])
        except Exception as e:
            print(e)
            # just restart it... maybe a timeout from discord!
            self.start()
            pass

    async def _as_secret_send(self, message):
        if message:
            if isinstance(message, str):
                await self.secret_context.discord_client.send_message(
                    self.secret_context.secret_channel, message)
            elif isinstance(message, discord.Embed):
                await self.secret_context.discord_client.send_message(
                    self.secret_context.secret_channel, embed=message)

    async def _restart(self):
        print('----------------------------')
        print('secRet bot is now restarting')
        print('----------------------------')
        await self.secret_context.discord_client.send_message(
            self.secret_context.secret_channel,
            embed=utils.simple_embed('restart', 'restarting secRet dBot',
                                     utils.random_color()))
        os.execv(sys.executable, [sys.executable.split("/")[-1]] + sys.argv)


def main():
    sdb = SecRetDBot()
    sdb.start()


if __name__ == "__main__":
    main()
