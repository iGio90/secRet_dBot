import discord


def is_admin(member):
    for role in member.roles:
        if role.name == 'Admins':
            return True
    return False


def is_dev(member):
    for role in member.roles:
        if role.name == 'Devs':
            return True
    return False


def is_bot(member):
    for role in member.roles:
        if role.name == 'BOT':
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


def build_default_embed(title, description, color):
    embed = discord.Embed(title=title, type='rich',
                          description=description,
                          color=color)
    embed.set_thumbnail(url="http://paulcilwa.com/Content/Science/Science.png")
    embed.set_author(name="secRet", url="https://secret.re")
    return embed
