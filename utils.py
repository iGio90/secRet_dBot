import discord


def is_admin(user_id):
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
