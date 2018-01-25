import json

import requests

import utils

API_KEY = 'r9y8rIbtIgB7p64eH1GzyoQc50jar2Z6'


async def on_message(message, discord_client, bus):
    parts = message.content.split(" ")
    if len(parts) < 2:
        # print the help
        bus.emit('secret_command', command='!help gif')
    else:
        if parts[1] == 'random':
            r = requests.get('http://api.giphy.com/v1/gifs/random?api_key=' + API_KEY)
            if r.status_code == 200:
                rs = json.loads(r.content.decode('utf8'))
                embed = utils.simple_embed('gif', 'random', utils.random_color())
                embed.set_image(url=rs['data']['image_url'])
                await discord_client.send_message(message.channel, embed=embed)
        elif parts[1] == 'search':
            try:
                q = str.join(" ", parts[2])
                off = 0
                if len(parts) > 3:
                    try:
                        off = int(parts[3])
                    except Exception as e:
                        pass
                r = requests.get('http://api.giphy.com/v1/gifs/search?api_key=' + API_KEY + '&q=' + q +
                                 '&limit=1&offset=' + str(off))
                if r.status_code == 200:
                    rs = json.loads(r.content.decode('utf8'))
                    for item in rs['data']:
                        embed = utils.simple_embed(item['slug'], item['source'], utils.random_color())
                        embed.set_image(url=item['images']['original']['url'])
                        await discord_client.send_message(message.channel, embed=embed)
            except Exception as e:
                pass

