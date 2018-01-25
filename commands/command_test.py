import discord
import requests
import utils


class TestCMD(object):
    def __init__(self, discord_client, mongo_db, bus, git_client, git_repo):
        self.discord_client = discord_client
        self.mongo_db = mongo_db
        self.bus = bus
        self.git_client = git_client
        self.git_repo = git_repo

    async def on_message(self, message):
        try:
            cmd = message.content
            if cmd.startswith('http'):
                r = requests.get(cmd)
                if r.status_code == 200:
                    cmd = r.content.decode('utf8')
            elif cmd.startswith("```python"):
                cmd = cmd.replace('```python', '')
                cmd = cmd.replace('```', '')
            if cmd is not None:
                print(cmd)
                exec(cmd)
        except Exception as e:
            embed = utils.simple_embed('error', e, discord.Color.red())
            await self.discord_client.send_message(message.channel, embed=embed)
