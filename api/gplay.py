import discord
import utils

from gplaycli import gplaycli


class GPlay(object):
    def __init__(self):
        self.play_icon_url = 'https://www.androidpolice.com/wp-content/uploads/2017/05/' \
                         'nexus2cee_ic_launcher_play_store_new-1.png'
        self.cli = gplaycli.GPlaycli(config_file='play_configs.conf')
        self.cli.token_enable = True
        self.cli.token, self.cli.gsfid = self.cli.retrieve_token()
        self.cli.token_url = "https://matlink.fr/token/email/gsfid"

    async def on_message(self, message, discord_client, bus):
        parts = message.content.split(" ")
        if len(parts) < 2:
            # print the help
            bus.emit('secret_command', command='!help gplay')
        else:
            if len(parts) > 2:
                q = str.join(" ", parts[2:])
                if parts[1] == 'search':
                    results = self.cli.search(q, 10)
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
                            embed.add_field(name='downloads', value=pkg[3])
                            embed.add_field(name='size', value=pkg[2])
                            embed.add_field(name='version', value=pkg[6])
                            embed.add_field(name='rating', value=pkg[7])
                            await discord_client.send_message(message.channel, embed=embed)
                elif parts[2] == 'info':
                    pass
