import subprocess

import discord


def build_default_embed(title, description, color, icon=True):
    embed = discord.Embed(title=title, type='rich',
                          description=description,
                          color=color)
    if icon:
        embed.set_thumbnail(url="http://paulcilwa.com/Content/Science/Science.png")
    embed.set_author(name="secRet", url="https://secret.re")
    return embed


def build_commands_embed(map, title, color):
    embed = build_default_embed('', '', color, icon=False)
    embed.add_field(name=title, value='-', inline=False)
    for cmd_name, cmd in map.items():
        description = ''
        if 'description' in cmd:
            description = cmd['description']
        embed.add_field(name="!" + cmd_name, value=description, inline=False)
    return embed


def is_admin(member):
    for role in member.roles:
        if role.name == 'Admins':
            return True
    return False


def is_bot(member):
    for role in member.roles:
        if role.name == 'BOT':
            return True
    return False


def is_dev(member):
    for role in member.roles:
        if role.name == 'Devs':
            return True
    return False


def is_owner(user_id):
    """
    :param user_id
    the id to check

    :return:
    true for admins
    """
    return user_id in [
        '168018245943558144'
    ]


def run_shell_command(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         shell=True, universal_newlines=True)
    return iter(p.stdout.readline, b'')
