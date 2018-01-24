import discord
import utils
import wikipedia


WIKI_ICON = 'https://upload.wikimedia.org/wikipedia/foundation/thumb/2/20/' \
            'Wikipedia-logo-v2-en_SVG.svg/200px-Wikipedia-logo-v2-en_SVG.svg.png'


async def on_message(message, discord_client, bus):
    parts = message.content.split[" "]
    p_len = len(parts)
    if p_len < 2:
        # print the help
        bus.emit('secret_command', command='!help wiki')
    elif p_len > 2:
        cmd = parts[1]
        if cmd == 'search':
            q = str.join(" ", parts[2:])
            r = wikipedia.search(q)
            if len(r) > 0:
                embed = utils.simple_embed('wikipedia', 'search results for: **' + q + '**',
                                           discord.Color.lighter_grey())
                embed.set_thumbnail(url=WIKI_ICON)
                for result in r:
                    embed.add_field(name=result, value='!wikipedia fetch **' + result + '**')
                await discord_client.send_message(message.channel, embed=embed)
            else:
                embed = utils.simple_embed('wikipedia', 'no results for: **' + q + '**',
                                           discord.Color.red())
                embed.set_thumbnail(url=WIKI_ICON)
                await discord_client.send_message(message.channel, embed=embed)

