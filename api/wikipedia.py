import discord
import os
import requests
import utils
import wikipedia

from colorthief import ColorThief


WIKI_ICON = 'https://upload.wikimedia.org/wikipedia/foundation/thumb/2/20/' \
            'Wikipedia-logo-v2-en_SVG.svg/200px-Wikipedia-logo-v2-en_SVG.svg.png'


async def on_message(message, discord_client, bus):
    parts = message.content.split(" ")
    p_len = len(parts)
    if p_len < 2:
        # print the help
        bus.emit('secret_command', command='!help wiki')
    elif p_len > 2:
        cmd = parts[1]
        q = str.join(" ", parts[2:])
        if cmd == 'search':
            r = wikipedia.search(q)
            if len(r) > 0:
                embed = utils.simple_embed('wikipedia', 'search results for: **' + q + '**',
                                           discord.Color.lighter_grey())
                embed.set_thumbnail(url=WIKI_ICON)
                for result in r:
                    embed.add_field(name=result, value='!wikipedia fetch **' + result + '**', inline=False)
                await discord_client.send_message(message.channel, embed=embed)
            else:
                embed = utils.simple_embed('wikipedia', 'no results for: **' + q + '**',
                                           discord.Color.red())
                embed.set_thumbnail(url=WIKI_ICON)
                await discord_client.send_message(message.channel, embed=embed)
        elif cmd == 'fetch':
            try:
                r = wikipedia.page(q)
                color = utils.random_color()
                img = WIKI_ICON
                if len(r.images) > 0:
                    m_img = r.images
                    f_img = None
                    while len(m_img) > 0:
                        img = m_img[0]
                        m_img.pop(0)
                        if str(img).endswith('.png') or str(img).endswith('.jpg') or str(img).endswith('.jpeg'):
                            f_img = img
                            break

                    if f_img:
                        response = requests.get(img)
                        if response.status_code == 200:
                            if not os.path.exists('files'):
                                os.mkdir('files')
                            with open("files/tmp_wiki_icon.png", 'wb') as f:
                                f.write(response.content)
                            color_thief = ColorThief("files/tmp_wiki_icon.png")
                            dominant_color = color_thief.get_color(quality=1)
                            color = int(utils.rgb_to_hex(dominant_color), 16)
                embed = utils.simple_embed(q, r.summary, color)
                embed.set_thumbnail(url=img)
                await discord_client.send_message(message.channel, embed=embed)
            except wikipedia.PageError as e:
                embed = utils.simple_embed('wikipedia', 'no results for: **' + q + '**',
                                           discord.Color.red())
                embed.set_thumbnail(url=WIKI_ICON)
                await discord_client.send_message(message.channel, embed=embed)
            except wikipedia.DisambiguationError as e:
                embed = utils.simple_embed('wikipedia', 'no results for: **' + q + '**. Use !wiki search *keywords and '
                                                                                   'provide a working page to fetch.',
                                           discord.Color.red())
                embed.set_thumbnail(url=WIKI_ICON)
                await discord_client.send_message(message.channel, embed=embed)

