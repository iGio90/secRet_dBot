import random
import subprocess

import discord
import math

ICON = "https://steemit-production-imageproxy-upload.s3.amazonaws.com/DQmVyhQzqP7TF1SKuDWJkY3HuEGzv3ZpWGzLoJSAk42E81w"
REPO = "https://github.com/secRetDBot/secRet_dBot"
REPO_SHORT = "secRetDBot/secRet_dBot"


def build_default_embed(title, description, color, icon=True, author=True):
    embed = discord.Embed(title=title, type='rich',
                          description=description,
                          color=color)
    if icon:
        embed.set_thumbnail(url=ICON)
    if author:
        embed.set_author(name="secret.re", url="https://secret.re")
    return embed


def build_commands_embed(map, title, color):
    embed = build_default_embed(title, '** **', color, icon=False, author=False)
    for cmd_name, cmd in map.items():
        description = '** **'
        if 'description' in cmd:
            description = cmd['description']
        embed.add_field(name="!" + cmd_name, value=description, inline=False)
    return embed


def clamp(x):
    return max(0, min(x, 255))


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


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


def random_color():
    return int('0x{:06x}'.format(random.randint(0, 256 ** 3)), 16)


def rgb_to_hex(rgb_tuple):
    return "{0:02x}{1:02x}{2:02x}".format(clamp(rgb_tuple[0]), clamp(rgb_tuple[1]), clamp(rgb_tuple[2]))


def run_shell_command(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         shell=True, universal_newlines=True)
    return iter(p.stdout.readline, b'')


def simple_embed(title, description, color):
    embed = discord.Embed(title=title, type='rich',
                          description=description,
                          color=color)
    return embed
