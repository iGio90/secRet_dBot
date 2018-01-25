import discord
import execjs
import requests
import utils


class TestCMD(object):
    def __init__(self, discord_client, mongo_db, bus, git_client, git_repo):
        self.discord_client = discord_client
        self.mongo_db = mongo_db
        self.bus = bus
        self.git_client = git_client
        self.git_repo = git_repo

        self.supported_languages = ['python', 'javascript']

    async def on_message(self, message, lang):
        try:
            cmd = message.content
            if lang == 'python':
                cmd = cmd.replace('```python', '')
                cmd = cmd.replace('```', '')
                exec(cmd)
            elif lang == 'javascript':
                execjs.eval(cmd)
            # await self.discord_client.delete_message(message)
        except Exception as e:
            embed = utils.simple_embed('error', e, discord.Color.red())
            await self.discord_client.send_message(message.channel, embed=embed)
