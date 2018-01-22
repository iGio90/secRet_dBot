import asyncio
import discord
import hurry
import utils


from datetime import datetime, timedelta


async def bot_status(discord_client, start_time, secret_channel):
    embed = discord.Embed(title='bot status', type='rich',
                          description='*',
                          color=utils.random_color())
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/"
                            "thumb/3/30/Icons8_flat_clock.svg/2000px-Icons8_flat_clock.svg.png")
    embed.set_author(name="secRet", url="https://secret.re",
                     icon_url="http://paulcilwa.com/Content/Science/Science.png")
    datetime_now = datetime.now()
    now = '{0:%H:%M:%S}'.format(datetime_now)
    uptime = str(timedelta(seconds=int(datetime_now.timestamp() - start_time)))

    embed.add_field(name='time', value=now, inline=True)
    embed.add_field(name='uptime', value=uptime, inline=True)
    await discord_client.send_message(secret_channel, embed=embed)


async def mongo_status(discord_client, mongo_db, secret_channel):
    mongo_status = mongo_db.command("serverStatus")
    db_stats = mongo_db.command("dbStats")
    embed = discord.Embed(title='mongo status', type='rich',
                          description='*',
                          color=utils.random_color())
    embed.set_thumbnail(url="https://www.todobackend.com/images/logos/mongodb.png")
    embed.set_author(name="secRet", url="https://secret.re",
                     icon_url="http://paulcilwa.com/Content/Science/Science.png")
    embed.add_field(name='host', value=mongo_status['host'], inline=True)
    embed.add_field(name='version', value=mongo_status['version'], inline=True)
    embed.add_field(name='process', value=mongo_status['process'], inline=True)
    embed.add_field(name='pid', value=mongo_status['pid'], inline=True)
    embed.add_field(name='db', value=db_stats['db'], inline=True)
    embed.add_field(name='collections', value=str(db_stats['collections']), inline=True)
    embed.add_field(name='objects', value=str(db_stats['objects']), inline=True)
    embed.add_field(name='indexes', value=str(db_stats['indexes']), inline=True)
    embed.add_field(name='sizes', value="-", inline=False)
    embed.add_field(name='storage', value=utils.convert_size(db_stats['storageSize']), inline=True)
    embed.add_field(name='objects', value=utils.convert_size(db_stats['indexSize']), inline=True)
    await discord_client.send_message(secret_channel, embed=embed)


async def secret_status(message, discord_client, mongo_db, start_time, secret_channel):
    await bot_status(discord_client, start_time, secret_channel)
    await mongo_status(discord_client, mongo_db, secret_channel)
