import discord
import execjs
from secret import utils


class TestCMD(object):
    def __init__(self, secret_context):
        self.secret_context = secret_context
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
            embed = utils.simple_embed('error', str(e), discord.Color.red())
            await self.secret_context.discord_client.send_message(message.channel, embed=embed)
