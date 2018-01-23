import discord

from commands import commands_analytics


async def handle(client, message):
    commands = message.content[1:].split(" ")
    if len(commands) < 2:
        embed = discord.Embed(title='statsroyale commands', type='rich',
                              description="** **",
                              color=discord.Colour.light_grey())
        embed.set_thumbnail(url="http://lh3.googleusercontent.com/3dnqf0Te-6_"
                                "SucM52DR3KhvlM2z46mRIMr8K5KYJlZq0Xbei6JDjkbHWRWQHtkhnk5yS=w300")
        embed.add_field(name="!statsroyale android_stats", value="print statistics from android app", inline=False)
        await client.send_message(message.channel, embed=embed)
    else:
        if commands[1] == 'android':
            if len(commands) > 2:
                if commands[2] == 'stat' or commands[2] == 'stats':
                    reports = commands_analytics.get_reports()

                    embed = discord.Embed(title='statsroyale', type='rich',
                                          description="daily android sessions",
                                          color=discord.Colour.green())
                    embed.set_thumbnail(url="http://lh3.googleusercontent.com/3dnqf0Te-6_"
                                            "SucM52DR3KhvlM2z46mRIMr8K5KYJlZq0Xbei6JDjkbHWRWQHtkhnk5yS=w300")
                    for stat in reports:
                        m = stat[0]
                        if stat[0] == 'ga:users':
                            m = 'daily sessions'
                        embed.add_field(name=m, value=str(stat[1]), inline=True)
                    await client.send_message(message.channel, embed=embed)
