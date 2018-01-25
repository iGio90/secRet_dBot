import discord
import os
import requests
from secret import utils

from colorthief import ColorThief
from gplaycli import gplaycli


class GPlay(object):
    def __init__(self):
        self.play_icon_url = 'https://www.androidpolice.com/wp-content/uploads/2017/05/' \
                         'nexus2cee_ic_launcher_play_store_new-1.png'
        self.cli = gplaycli.GPlaycli(config_file='play_configs.conf')
        self.cli.token_enable = True
        self.cli.token_url = "https://matlink.fr/token/email/gsfid"
        self.cli.token, self.cli.gsfid = self.cli.retrieve_token()
        self.cli.connect()

    async def fetch(self, message, discord_client, package_name):
        try:
            store_info = self.cli.api.details(package_name)

            icon = None
            color = utils.random_color()

            for img in store_info['images']:
                if img['imageType'] == 4:
                    icon = img['url']
                    break
            if icon:
                response = requests.get(icon)
                if response.status_code == 200:
                    if not os.path.exists('files'):
                        os.mkdir('files')
                    with open("files/tmp_gplay_icon.png", 'wb') as f:
                        f.write(response.content)
                    color_thief = ColorThief("files/tmp_gplay_icon.png")
                    dominant_color = color_thief.get_color(quality=1)
                    color = int(utils.rgb_to_hex(dominant_color), 16)

            embed = utils.simple_embed(store_info['title'], store_info['docId'], color)
            if icon:
                embed.set_thumbnail(url=icon)
            embed.add_field(name='author', value=store_info['author'])
            embed.add_field(name='version code', value=str(store_info['versionCode']))
            embed.add_field(name='uploaded', value=store_info['uploadDate'])
            embed.add_field(name='downloads', value=store_info['numDownloads'].replace('downloads', ''))
            embed.add_field(name='rating', value=str(store_info['aggregateRating']['starRating']))
            embed.add_field(name='comments', value=str(store_info['aggregateRating']['commentCount']))
            embed.add_field(name='type', value=store_info['category']['appType'])
            embed.add_field(name='category', value=store_info['category']['appCategory'])
            await discord_client.send_message(message.channel, embed=embed)
        except gplaycli.RequestError as e:
            embed = utils.simple_embed('google play', 'package **' + package_name + '** not found',
                                       discord.Color.red())
            embed.set_thumbnail(url=self.play_icon_url)
            await discord_client.send_message(message.channel, embed=embed)
        except Exception as e:
            embed = utils.simple_embed('google play', 'error on package **' + package_name + '**. ' + str(e),
                                       discord.Color.red())
            embed.set_thumbnail(url=self.play_icon_url)
            await discord_client.send_message(message.channel, embed=embed)

    async def on_message(self, message, secret_context):
        parts = message.content.split(" ")
        if len(parts) < 2:
            # print the help
            bus.emit('secret_command', command='!help gplay')
        else:
            if len(parts) > 2:
                if parts[1] == 'search':
                    q = str.join(" ", parts[2:])
                    await self.search(message, secret_context.discord_client, q)
                elif parts[1] == 'fetch':
                    await self.fetch(message, secret_context.discord_client, parts[2])

    async def search(self, message, discord_client, q):
        results = self.cli.search(q, 3)
        if results is None:
            embed = utils.simple_embed('google play', 'no apps found for: **' + q + '**',
                                       discord.Color.red())
            embed.set_thumbnail(url=self.play_icon_url)
            await discord_client.send_message(message.channel, embed=embed)
        else:
            # remove headers
            results.pop(0)

            embed = utils.simple_embed('google play', 'results for: **' + q + '**', discord.Color.red())
            embed.set_thumbnail(url=self.play_icon_url)
            await discord_client.send_message(message.channel, embed=embed)
            for pkg in results:
                embed = utils.simple_embed(pkg[0], pkg[5], utils.random_color())
                embed.add_field(name='creator', value=pkg[1])
                embed.add_field(name='last update', value=pkg[4])
                embed.add_field(name='downloads', value=pkg[3].replace(' downloads', ''))
                embed.add_field(name='size', value=pkg[2])
                embed.add_field(name='version', value=pkg[6])
                embed.add_field(name='rating', value=pkg[7])
                await discord_client.send_message(message.channel, embed=embed)
