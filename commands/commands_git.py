import discord


def build_commit_list_embed(git_repo):
    """
    :param: git_repo
    the repo object
    :return:
    an embed discord object with the latest 10 commits
    """
    embed = discord.Embed(title='secRet', type='rich', description='Last 10 commits',
                          color=discord.Colour(0xA2746A))
    embed.set_thumbnail(url="https://octodex.github.com/images/heisencat.png")
    embed.set_author(name="iGio90/secRet-dBot", url="https://github.com/iGio90/secRet_dBot",
                     icon_url="http://paulcilwa.com/Content/Science/Science.png")
    k = 0
    for commit in git_repo.get_commits():
        if k == 10:
            break
        commit_date = '{0:%Y-%m-%d %H:%M:%S}'.format(commit.commit.author.date)
        embed.add_field(name=commit.commit.message,
                        value=commit.commit.author.name + " - " + commit_date,
                        inline=False)
        k += 1
    return embed


def get_last_commit(git_repo):
    """
    :param git_repo:
    the repo object
    :return:
    the last commit
    """
    return git_repo.get_commits()[0]
