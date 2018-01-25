import discord

from secret import utils


async def commands(message, discord_client, admin_commands_map, dev_commands_map, commands_map, shortcuts_map):
    parts = message.content.split(" ")
    if len(parts) < 2:
        embed = utils.build_default_embed('commands', '** **', discord.Color.gold(), icon=False, author=False)
        embed.add_field(name="!commands admin", value='admin commands', inline=False)
        embed.add_field(name="!commands dev", value='dev commands', inline=False)
        embed.add_field(name="!commands user", value='user commands', inline=False)
        await discord_client.send_message(message.channel, embed=embed)
    else:
        found = False
        if parts[1] in shortcuts_map:
            parts[1] = shortcuts_map[parts[1]]
            
        if parts[1] == 'admin' or parts[1] == 'admins':
            # admin commands
            found = True
            embed = utils.build_commands_embed(admin_commands_map, 'admin commands', discord.Color.red())
            await discord_client.send_message(message.channel, embed=embed)
        elif parts[1] == 'dev' or parts[1] == 'devs':
            # dev commands
            found = True
            embed = utils.build_commands_embed(dev_commands_map, 'dev commands', discord.Color.blue())
            await discord_client.send_message(message.channel, embed=embed)
        elif parts[1] == 'user' or parts[1] == 'users':
            # user commands
            found = True
            embed = utils.build_commands_embed(commands_map, 'user commands', discord.Color.light_grey())
            await discord_client.send_message(message.channel, embed=embed)
        if found:
            # help hint for sub commands
            embed = utils.build_default_embed('!help *command_name', 'print additional info for a specific command',
                                              discord.Color.green(), icon=False, author=False)
            await discord_client.send_message(message.channel, embed=embed)


async def help(message, discord_client, cmd_maps, shortcuts_map):
    """
    :param message:
    discord message
    :param discord_client:
    discord client
    :param cmd_maps:
    array with all command maps
    :return:
    """
    parts = message.content.split(" ")
    if len(parts) < 2:
        embed = discord.Embed(title='', type='rich',
                              description="goal is to build me as an automated **bot** with whatever feature "
                                          "people would like to code. I'll soon run on a virtual"
                                          " machine with **root** privileges,"
                                          "but meanwhile, I can already do something:\n\n** **",
                              color=discord.Colour.dark_red())
        embed.set_thumbnail(url=utils.ICON)
        embed.set_author(name="secRet", url="https://secret.re")
        embed.add_field(name="!commands", value="something to interact with me", inline=False)
        embed.add_field(name="!devme", value="info and help about coding features", inline=False)
        embed.add_field(name="!rules", value="a world without rules... mhhh chaos", inline=False)
        await discord_client.send_message(message.channel, embed=embed)
    else:
        cmd = parts[1]
        found = False

        if cmd in shortcuts_map:
            cmd = shortcuts_map[cmd]

        for map in cmd_maps:
            if cmd in map:
                found = True
                cmd_object = map[cmd]
                color = utils.random_color()
                embed = discord.Embed(title=cmd, type='rich',
                                      description=cmd_object['description'],
                                      color=color)
                if 'author' in cmd_object:
                    embed.add_field(name='author', value=cmd_object['author'], inline=False)
                await discord_client.send_message(message.channel, embed=embed)
                if 'sub_commands' in cmd_object:
                    embed = discord.Embed(title='sub commands', type='rich',
                                          description='** **',
                                          color=color)
                    for sub in cmd_object['sub_commands']:
                        description = '** **'
                        if 'description' in sub:
                            description = sub['description']
                        embed.add_field(name='!' + cmd + ' ' + sub['name'], value=description, inline=False)
                    await discord_client.send_message(message.channel, embed=embed)
                break
        if not found:
            embed = utils.simple_embed('error', 'command not found', discord.Color.red())
            await discord_client.send_message(message.channel, embed=embed)
