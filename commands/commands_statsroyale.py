import discord

from commands import commands_analytics


async def handle(client, message):
    commands = message.content[1:].split(" ")
    if len(commands) == 1:
        embed = discord.Embed(title='', type='rich',
                              description="statsroyale commands",
                              color=discord.Colour.light_grey())
        embed.set_thumbnail(url="https://lh3.googleusercontent.com"
                                "/8KbtL9JeCBi1iDOGhOQDbZ3uZC84lMLA5G_ZfW6b5hRMIvzsMvBAHCZfjBS5Khxykg=w300")
        embed.set_author(name="secRet", url="https://secret.re")
        embed.add_field(name="!statsroyale android_stats", value="print statistics from android app", inline=False)
        await client.send_message(message.channel, embed=embed)
    else:
        sub = commands[1]
        if sub == 'android_stats':
            reports = commands_analytics.get_reports()

            embed = discord.Embed(title='statsroyale', type='rich',
                                  description="daily android sessions",
                                  color=discord.Colour.green())
            embed.set_thumbnail(url="https://lh3.googleusercontent.com"
                                    "/8KbtL9JeCBi1iDOGhOQDbZ3uZC84lMLA5G_ZfW6b5hRMIvzsMvBAHCZfjBS5Khxykg=w300")
            for stat in reports:
                m = stat[0]
                if stat[0] == 'ga:users':
                    m = 'daily sessions'
                embed.add_field(name=m, value=str(stat[1]), inline=True)
            await client.send_message(message.channel, embed=embed)
