import discord
import time

import utils

from mongo_models import pull_vote, user


def calculate_pr_points(git_user_id, git_user_name, message):
    try:
        user_doc = user.User.objects.get(git_user_id=git_user_id)
    except user.DoesNotExist as e:
        try:
            user_doc = user.User(git_user_id=git_user_id,
                                 git_user_name=git_user_name)
            user_doc.save()
        except Exception as e:
            return -1

    points = user_doc.points
    m_c = len(message.server.members)
    req = 0.7 * m_c
    if points > 0:
        dec = points / (m_c / 50)
        n_req = req - dec

        # check if the new req points are less than 0.
        # add 10% of the total users
        if req < 0:
            req = m_c % 10

        # if the new req points is less than the 50% of the original ones
        # let's add a 10%
        if n_req < req % 50:
            n_req += req % 10
    return float("{0:.2f}".format(req))


def calculate_vote_points(message, votes, required_points):
    try:
        user_doc = user.User.objects.get(discord_id=message.author.id)
        m_c = len(message.server.members)
        points = user_doc.points
        if utils.is_admin(message.author):
            points += (m_c * 4) / (m_c / 10)
        elif utils.is_dev(message.author):
            points += (m_c * 2) / (m_c / 10)

        if points > required_points and votes < 1:
            # an unique vote can't approve a pr
            # min is 2 even for admins
            # grant the 90% of the points
            points = float("{0:.2f}".format(required_points * 90 / 100))
        return points, user_doc.discord_name
    except user.DoesNotExist as e:
        return -1
    except Exception as e:
        return -1


async def check_merge(message, discord_client, db_pull_doc, git_repo):
    if db_pull_doc.points >= db_pull_doc.required_points:
        await merge_pr(message, discord_client, git_repo, db_pull_doc)


def get_last_commit(git_repo):
    """
    :param git_repo:
    the repo object
    :return:
    the last commit
    """
    return git_repo.get_commits()[0]


async def get_last_commits(message, discord_client, git_repo):
    """
    :param: git_repo
    the repo object
    :return:
    an embed discord object with the latest 10 commits
    """
    embed = discord.Embed(title='recent secRet dBot commits', type='rich', description='',
                          color=discord.Colour(0xA2746A))
    embed.set_author(name=utils.REPO_SHORT, url=utils.REPO, icon_url=utils.ICON)
    k = 0
    for commit in git_repo.get_commits():
        if k == 10:
            break
        commit_date = '{0:%Y-%m-%d %H:%M:%S}'.format(commit.commit.author.date)
        embed.add_field(name=commit.commit.message,
                        value=commit.commit.author.name + " - " + commit_date,
                        inline=False)
        k += 1
    await discord_client.send_message(message.channel, embed=embed)


async def git(message, discord_client, git_client, git_repo, bus):
    parts = message.content.split(" ")

    if len(parts) < 2:
        await print_git_help(bus)
    else:
        if parts[1] == 'commits':
            await get_last_commits(message, discord_client, git_repo)
        elif parts[1] == 'link':
            await link_git(message, discord_client, git_client)
        elif parts[1] == 'search':
            try:
                what = parts[2]
                if what == 'user':
                    try:
                        git_user = git_client.legacy_search_users(parts[3])[0]
                        embed = discord.Embed(title="search result",
                                              type='rich',
                                              description=parts[3],
                                              color=utils.random_color())
                        embed.set_author(name=git_user.login, url='https://github.com/' + git_user.login)
                        embed.set_thumbnail(url=git_user.avatar_url)
                        embed.add_field(name='id', value=str(git_user.id), inline=False)
                        if git_user.type is not None:
                            embed.add_field(name='type', value=git_user.type)
                        embed.add_field(name='followers', value=str(git_user.followers))
                        if git_user.contributions is not None:
                            embed.add_field(name='contributions', value=str(git_user.contributions))
                        if git_user.bio is not None:
                            embed.add_field(name='bio', value=git_user.bio, inline=False)
                        await discord_client.send_message(message.channel, embed=embed)
                    except Exception as e:
                        embed = utils.simple_embed('info', 'no user found', discord.Color.blue())
                        await discord_client.send_message(message.channel, embed=embed)
            except Exception as e:
                # just don't reply
                pass
        elif parts[1] == 'unlink':
            try:
                user.User.objects.get(discord_id=message.author.id).delete()
                embed = utils.simple_embed('success', 'you are now unlinked and your points are back to 0',
                                           discord.Color.green())
                await discord_client.send_message(message.channel, embed=embed)
            except user.DoesNotExist:
                embed = utils.simple_embed('info', 'you are not linked with any github id', discord.Color.blue())
                await discord_client.send_message(message.channel, embed=embed)


async def link_git(message, discord_client, git_client):
    parts = message.content.split(" ")
    try:
        git_nick_name = parts[2]
        try:
            u = user.User.objects.get(discord_id=message.author.id)
            embed = utils.simple_embed('info', 'you are already linked to **' + u.git_user_name + '**',
                                       discord.Color.blue())
            await discord_client.send_message(message.channel, embed=embed)
        except user.DoesNotExist:
            try:
                git_user = git_client.legacy_search_users(git_nick_name)[0]
                r = 'yes'
                if r == 'yes' or r == 'y':
                    u = user.User(git_user_id=git_user.id,
                                  git_user_name=git_user.login,
                                  discord_id=message.author.id,
                                  discord_name=message.author.display_name,
                                  discord_mention=message.author.mention)

                    try:
                        u.save()
                        embed = utils.simple_embed('success', u.git_user_name + ' has been linked to ' +
                                                   message.author.id,
                                                   discord.Color.green())
                        await discord_client.send_message(message.channel, embed=embed)
                    except user.NotUniqueError as e:
                        u = user.User.objects.get(git_user_id=git_user.login)
                        embed = utils.simple_embed('error', '**' + git_user.login + '** already linked with: ' +
                                                   str(u.discord_id), discord.Color.red())
                        await discord_client.send_message(message.channel, embed=embed)
            except Exception as e:
                embed = utils.simple_embed('info', 'no user found', discord.Color.blue())
                await discord_client.send_message(message.channel, embed=embed)
    except Exception as e:
        desc = 'link your github with **!git link *git_user_name**'
        await discord_client.send_message(message.channel,
                                          embed=utils.simple_embed('info', desc, discord.Color.blue()))
        embed = utils.simple_embed('error', desc, discord.Color.blue())
        await discord_client.send_message(message.channel, embed=embed)
        pass


async def merge_pr(message, discord_client, git_repo, db_pull_doc):
    git_pr = git_repo.get_pull(db_pull_doc.pull_number)
    if git_pr and git_pr.mergeable:
        embed = discord.Embed(title=db_pull_doc.pull_title, type='rich', description=db_pull_doc.user_name,
                              color=discord.Color.green())
        for discord_id, vote in db_pull_doc.votes.items():
            embed.add_field(name=vote['name'],
                            value=str(vote['points']),
                            inline=True)
        await discord_client.send_message(message.channel, embed=embed)

        status = git_pr.merge()
        if status.merged:
            db_pull_doc.delete()
            embed = utils.simple_embed('success',
                                       status.sha + ' **merged**. scheduled for next auto-update',
                                       discord.Color.green())
            await discord_client.send_message(message.channel, embed=embed)
            await on_post_merge(message, discord_client, db_pull_doc)
        else:
            embed = utils.simple_embed('error',
                                       status.message,
                                       discord.Color.red())
            await discord_client.send_message(message.channel, embed=embed)
    else:
        if git_pr.merge:
            embed = utils.simple_embed('info',
                                       'the pr has already been merged',
                                       discord.Color.blue())
        else:
            embed = utils.simple_embed('error',
                                       'the pr can\'t be merged. check conflicts and resolve them!',
                                       discord.Color.green())
        await discord_client.send_message(message.channel, embed=embed)


async def on_post_merge(message, discord_client, db_pull_doc):
    try:
        user_doc = user.User.objects.get(git_user_id=db_pull_doc.user_id)
        reward_points = db_pull_doc.required_points / 15.5
        reward_points = float("{0:.2f}".format(reward_points))

        # add points
        user_doc.points += reward_points
        user_doc.points = float("{0:.2f}".format(user_doc.points))
        user_doc.save()

        if user_doc.discord_mention:
            desc = '**' + str(reward_points) + '** given to: **' + user_doc.discord_mention + '**'
        else:
            desc = '**' + str(reward_points) + '** given to: **' + user_doc.discord_name + '**'
        embed = utils.simple_embed('points attribution', desc, discord.Color.green())
        await discord_client.send_message(message.channel, embed=embed)
    except user.DoesNotExist as e:
        pass


async def pr(message, discord_client, git_repo):
    parts = message.content.split(" ")
    if len(parts) == 1:
        await print_pr_help(message, discord_client, git_repo)
    else:
        if parts[1] == 'check':
            try:
                id = int(parts[2])
                try:
                    db_pull_doc = pull_vote.PullVote.objects.get(pull_id=id)
                    if db_pull_doc.points >= db_pull_doc.required_points:
                        await check_merge(message, discord_client, db_pull_doc, git_repo)
                    else:
                        prq = git_repo.get_pull(db_pull_doc.pull_number)
                        await print_pr(message, discord_client, prq, db_pull_doc)
                except pull_vote.DoesNotExist as e:
                    await discord_client.send_message(message.channel,
                                                      embed=utils.simple_embed('error', 'pull request not found',
                                                                               discord.Color.red()))
            except Exception as e:
                await discord_client.send_message(message.channel,
                                                  embed=utils.simple_embed('error', 'usage: !pr check *pull_id',
                                                                           discord.Color.red()))
        elif parts[1] == 'downvote':
            try:
                id = int(parts[2])
                try:
                    db_pull_doc = pull_vote.PullVote.objects.get(pull_id=id)
                    vote_points = -1
                    user_name = ''
                    try:
                        vote_points, user_name = calculate_vote_points(message, len(db_pull_doc.votes),
                                                                       db_pull_doc.required_points)
                    except Exception as e:
                        pass
                    if vote_points < 0:
                        desc = 'link your github with **!git link *git_user_name**'
                        await discord_client.send_message(message.channel,
                                                          embed=utils.simple_embed('info', desc, discord.Color.blue()))
                    elif message.author.id in db_pull_doc.votes:
                        await discord_client.send_message(message.channel,
                                                          embed=utils.simple_embed('error', 'you already voted this pr',
                                                                                   discord.Color.red()))
                    else:
                        db_pull_doc.points -= vote_points
                        db_pull_doc.points = float("{0:.2f}".format(db_pull_doc.points))
                        db_pull_doc.votes[message.author.id] = {
                            'created': time.time(),
                            'name': user_name,
                            'points': vote_points,
                        }
                        db_pull_doc.save()
                        embed = utils.simple_embed('success', '**' + str(vote_points) +
                                                   '** points removed.\nTotal points: **' + str(db_pull_doc.points)
                                                   + '**' + '\nRequired points: **' + str(db_pull_doc.required_points)
                                                   + '**',
                                                   discord.Color.green())
                        await discord_client.send_message(message.channel, embed=embed)
                except pull_vote.DoesNotExist as e:
                    await discord_client.send_message(message.channel,
                                                      embed=utils.simple_embed('error', 'pull request not found',
                                                                               discord.Color.red()))
            except Exception as e:
                await discord_client.send_message(message.channel,
                                                  embed=utils.simple_embed('error', 'usage: !pr downvote *pull_id',
                                                                           discord.Color.red()))
        elif parts[1] == 'upvote':
            try:
                id = int(parts[2])
                try:
                    db_pull_doc = pull_vote.PullVote.objects.get(pull_id=id)
                    vote_points = -1
                    user_name = ''
                    try:
                        vote_points, user_name = calculate_vote_points(message, len(db_pull_doc.votes),
                                                                       db_pull_doc.required_points)
                    except Exception as e:
                        pass
                    if vote_points < 0:
                        desc = 'link your github with **!git link**'
                        await discord_client.send_message(message.channel,
                                                          embed=utils.simple_embed('info', desc, discord.Color.blue()))
                    elif message.author.id in db_pull_doc.votes:
                        await discord_client.send_message(message.channel,
                                                          embed=utils.simple_embed('error', 'you already voted this pr',
                                                                                   discord.Color.red()))
                    else:
                        db_pull_doc.points += vote_points
                        db_pull_doc.points = float("{0:.2f}".format(db_pull_doc.points))
                        if db_pull_doc.points >= db_pull_doc.required_points:
                            db_pull_doc.points = db_pull_doc.required_points

                        db_pull_doc.votes[message.author.id] = {
                            'created': time.time(),
                            'name': user_name,
                            'points': vote_points,
                        }
                        db_pull_doc.save()
                        embed = utils.simple_embed('success', '**' + str(vote_points) +
                                                   '** points added.\nTotal points: **' + str(db_pull_doc.points)
                                                   + '**' + '\nRequired points: **' + str(db_pull_doc.required_points)
                                                   + '**',
                                                   discord.Color.green())
                        await discord_client.send_message(message.channel, embed=embed)

                        if db_pull_doc.points >= db_pull_doc.required_points:
                            try:
                                u = user.User.objects.get(git_user_id=db_pull_doc.user_id)
                                embed = utils.simple_embed('success',
                                                           'pr ' + db_pull_doc.pull_title + ' by **' +
                                                           u.discord_mention + '** has been accepted.',
                                                           discord.Color.green())
                            except Exception as e:
                                embed = utils.simple_embed('success',
                                                           'pr ' + db_pull_doc.pull_title + ' by **' +
                                                           db_pull_doc.user_name + '** has been accepted.',
                                                           discord.Color.green())
                            await discord_client.send_message(message.channel, embed=embed)
                            await check_merge(message, discord_client, db_pull_doc, git_repo)
                except pull_vote.DoesNotExist as e:
                    await discord_client.send_message(message.channel,
                                                      embed=utils.simple_embed('error', 'pull request not found',
                                                                               discord.Color.red()))
            except Exception as e:
                await discord_client.send_message(message.channel,
                                                  embed=utils.simple_embed('error', 'usage: !pr upvote *pull_id',
                                                                           discord.Color.red()))


async def print_git_help(bus):
    bus.emit('secret_command', command='!help git')


async def print_pr(message, discord_client, prq, db_pull_doc):
    embed = discord.Embed(title=prq.user.login, type='rich', description=prq.title, url=prq.user.url,
                          color=discord.Colour(0xA2746A))
    embed.set_thumbnail(url=prq.user.avatar_url)
    created = '{0:%Y-%m-%d %H:%M:%S}'.format(prq.created_at)
    updated = '{0:%Y-%m-%d %H:%M:%S}'.format(prq.updated_at)
    embed.add_field(name='author', value=prq.user.login)
    embed.add_field(name='id', value=str(prq.id))
    embed.add_field(name='created', value=created)
    embed.add_field(name='last update', value=updated)
    embed.add_field(name='commits', value=str(prq.commits))
    embed.add_field(name='comments', value=str(prq.comments))

    embed.add_field(name='points', value=str(db_pull_doc.points))
    embed.add_field(name='required points', value=str(db_pull_doc.required_points))

    await discord_client.send_message(message.channel, embed=embed)


async def print_pr_help(message, discord_client, git_repo):
    embed = discord.Embed(title='pull requests list', type='rich',
                          description='',
                          color=discord.Colour(0xA2746A))
    embed.add_field(name='!pr check *pull_id', value="try to re-merge after conflict resolution", inline=False)
    embed.add_field(name='!pr upvote *pull_id', value="upvote a pull request", inline=True)
    embed.add_field(name='!pr downvote *pull_id', value="downvote a pull request", inline=True)
    await discord_client.send_message(message.channel, embed=embed)
    await print_pr_list(message, discord_client, git_repo)


async def print_pr_list(message, discord_client, git_repo):
    for prq in git_repo.get_pulls():
        if prq.closed_at:
            # do not add closed
            continue

        try:
            db_pull_doc = pull_vote.PullVote.objects.get(pull_id=prq.id)
        except pull_vote.DoesNotExist as e:
            req_points = calculate_pr_points(prq.user.id, prq.user.login, message)
            if req_points > 0:
                db_pull_doc = pull_vote.PullVote(pull_id=prq.id,
                                                 user_id=prq.user.id,
                                                 user_name=prq.user.login)
                db_pull_doc.pull_number = prq.number
                db_pull_doc.pull_title = prq.title
                db_pull_doc.required_points = req_points
                db_pull_doc.save()
            else:
                continue
        await print_pr(message, discord_client, prq, db_pull_doc)
