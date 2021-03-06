from datetime import datetime

import json
import requests
from secret import utils

API_KEY = 'srRLeAmTroxPinDG8Aus3Ikl6tLGJd94'


async def on_message(message, secret_context):
    parts = message.content.split(" ")
    try:
        location_code = int(parts[1])
        r = requests.get("https://api.accuweather.com/currentconditions/v1/" + str(location_code) +
                         "?apikey=" + API_KEY + "&details=true&getphotos=true")
        j = json.loads(r.content.decode('utf8'))
        if 'code' in j:
            embed = utils.simple_embed('accuweather', 'location id not found. use '
                                                      '!weather search *city_name to get the city code',
                                       utils.random_color())
            await secret_context.discord_client.send_message(message.channel, embed=embed)
        else:
            obj = j[0]
            embed = utils.simple_embed('accuweather', 'weather conditions for: **' + parts[1] + '**',
                                       utils.random_color())
            embed.add_field(name='condition', value=obj['WeatherText'], inline=False)
            embed.add_field(name='update time', value=datetime.fromtimestamp(obj['EpochTime'])
                            .strftime('%Y-%m-%d %H:%M:%S'), inline=False)
            ct = obj['Temperature']['Metric']['Value']
            cf = obj['Temperature']['Imperial']['Value']
            ct_r = obj['RealFeelTemperature']['Metric']['Value']
            cf_r = obj['RealFeelTemperature']['Imperial']['Value']

            embed.add_field(name='temperature', value=str(ct) + ' **C** | ' + str(cf) + ' **F**')
            embed.add_field(name='real feel', value=str(ct_r) + ' **C** | ' + str(cf_r) + ' **F**')
            embed.add_field(name='humidity', value=str(obj['RelativeHumidity']) + '%')
            embed.add_field(name='cloud cover', value=str(obj['CloudCover']) + '%')
            embed.add_field(name='wind direction', value=str(obj['Wind']['Direction']['Degrees']) +
                                                     obj['Wind']['Direction']['English'])
            embed.add_field(name='wind speed', value=str(obj['Wind']['Speed']['Metric']['Value']) + ' km/h')
            embed.set_thumbnail(url=obj['Photos'][0]['PortraitLink'])
            await secret_context.discord_client.send_message(message.channel, embed=embed)
    except Exception as e:
        if len(parts) < 1:
            embed = utils.simple_embed('accuweather', 'use !weather search *city_name to get the city code',
                                       utils.random_color())
            await secret_context.discord_client.send_message(message.channel, embed=embed)
        else:
            if len(parts) > 2 and parts[1] == 'search':
                parts = parts[2:]
                q = str.join(" ", parts)
                r = requests.get("https://api.accuweather.com/locations/v1/cities/autocomplete.json?apikey="
                                 + API_KEY + "&language=en&q=" + q)
                j = json.loads(r.content.decode('utf8'))
                if len(j) == 0:
                    embed = utils.simple_embed('accuweather', 'no city found for **' + q + '**',
                                               utils.random_color())
                    await secret_context.discord_client.send_message(message.channel, embed=embed)
                else:
                    embed = utils.simple_embed('accuweather', 'results for **' + q + '**',
                                               utils.random_color())
                    for city in j:
                        embed.add_field(name=city['LocalizedName'], value=city['Key'], inline=True)
                    await secret_context.discord_client.send_message(message.channel, embed=embed)
            else:
                embed = utils.simple_embed('accuweather', 'use !weather search *city_name to get the city code',
                                           utils.random_color())
                await secret_context.discord_client.send_message(message.channel, embed=embed)



