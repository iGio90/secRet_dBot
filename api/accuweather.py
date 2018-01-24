import discord
import json
import requests
import utils


API_KEY = 'srRLeAmTroxPinDG8Aus3Ikl6tLGJd94'


async def on_message(message, discord_client):
    parts = message.content.split(" ")
    try:
        location_code = int(message[1])
    except Exception as e:
        if len(parts) < 1:
            embed = utils.simple_embed('accuweather', 'use  !weather search *city_name to get the city code',
                                       utils.random_color())
            await discord_client.send_message(message.channel, embed=embed)
        else:
            if len(parts) > 2 and parts[2] == 'search':
                r = requests.get("https://api.accuweather.com/locations/v1/cities/autocomplete.json?apikey="
                                 + API_KEY + "&language=en&q=" + "milan")
                j = json.loads(r.content.decode('utf8'))
                if len(j) == 0:
                    embed = utils.simple_embed('accuweather', 'no city found for **' + parts[2] + '**',
                                               utils.random_color())
                    await discord_client.send_message(message.channel, embed=embed)
                else:
                    embed = utils.simple_embed('accuweather', 'results for **' + parts[2] + '**',
                                               utils.random_color())
                    for city in j:
                        embed.add_field(name=city['LocalizedName'], value=city['Key'], inline=True)
                    await discord_client.send_message(message.channel, embed=embed)


