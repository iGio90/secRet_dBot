import discord

from secret import utils


async def bot_status(secret_context):
    status = secret_context.handler_status.get_bot_status()
    embed = discord.Embed(title='bot status', type='rich',
                          description='** **',
                          color=utils.random_color())
    embed.set_thumbnail(url=status['icon'])

    embed.add_field(name='time', value=status['now'], inline=True)
    embed.add_field(name='uptime', value=status['uptime'], inline=True)
    await secret_context.discord_client.send_message(
        secret_context.secret_channel, embed=embed)


async def discord_status(secret_context):
    status = secret_context.handler_status.get_discord_status()
    embed = discord.Embed(title='discord status', type='rich',
                          description='** **',
                          color=utils.random_color())
    if status['connected']:
        embed.set_thumbnail(url=status['icon'])
        embed.add_field(name='id', value=status['id'], inline=True)
        embed.add_field(name='name', value=status['name'], inline=True)
        embed.add_field(name='created', value=status['created_at'], inline=True)
        embed.add_field(name='members', value=str(status['members']), inline=True)

    await secret_context.discord_client.send_message(
        secret_context.secret_channel, embed=embed)


async def git_status(secret_context):
    status = secret_context.handler_status.get_git_status()
    embed = discord.Embed(title='git status', type='rich',
                          description='*',
                          color=utils.random_color())
    embed.set_thumbnail(url=status['icon'])

    embed.add_field(name='status', value=status['status'], inline=True)
    embed.add_field(name='updated', value=status['updated'], inline=True)
    await secret_context.discord_client.send_message(
        secret_context.secret_channel, embed=embed)


async def mongo_status(secret_context):
    status = secret_context.handler_status.get_mongo_status()
    embed = discord.Embed(title='mongo status', type='rich',
                          description='*',
                          color=utils.random_color())
    embed.set_thumbnail(url=status['icon'])
    embed.add_field(name='host', value=status['host'], inline=True)
    embed.add_field(name='version', value=status['version'], inline=True)
    embed.add_field(name='process', value=status['process'], inline=True)
    embed.add_field(name='pid', value=status['pid'], inline=True)
    embed.add_field(name='db', value=status['db'], inline=True)
    embed.add_field(name='collections', value=str(status['collections']), inline=True)
    embed.add_field(name='objects', value=str(status['objects']), inline=True)
    embed.add_field(name='indexes', value=str(status['indexes']), inline=True)
    embed.add_field(name='sizes', value="-", inline=False)
    embed.add_field(name='storage', value=utils.convert_size(status['storage_size']), inline=True)
    embed.add_field(name='indexes', value=utils.convert_size(status['index_size']), inline=True)
    await secret_context.discord_client.send_message(
        secret_context.secret_channel, embed=embed)


async def secret_status(secret_context):
    await bot_status(secret_context)
    await discord_status(secret_context)
    await mongo_status(secret_context)
    await git_status(secret_context)
