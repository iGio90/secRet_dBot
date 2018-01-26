import time
import os
import discord

from secret import utils
from secret.discord_commands import commands_git
from datetime import datetime
from threading import Thread


class SecRet(Thread):
    def __init__(self, secret_context):
        self.secret_context = secret_context
        # get and hold last commit sha for auto update
        self.last_commit_sha = commands_git.get_last_commit(self.secret_context.git_repo).sha
        self.last_web_commit_sha = commands_git.get_last_commit(self.secret_context.web_repo).sha

        # register bus event
        self.secret_context.bus.add_event(self.secret_update, 'secret_update')

        Thread.__init__(self)

    def run(self):
        # sleep until 00 on first run
        now = datetime.now()
        c_min = now.minute
        c_sec = now.second
        l_min = 59 - c_min
        l_sec = 59 - c_sec + (60 * l_min)

        time.sleep(l_sec)

        while True:
            self.secret_hourly_task()
            time.sleep(60 * 60)

    def secret_hourly_task(self):
        # ping main thread
        self.secret_context.bus.emit('secret_ping')

        # check for update through git
        self.secret_update()

    def secret_update(self, print_no_update=False, web_update=False):
        if web_update:
            commits = self.secret_context.web_repo.get_commits()
        else:
            commits = self.secret_context.git_repo.get_commits()

        commit = commits[0]
        if not web_update and commit.sha != self.last_commit_sha:
            embed = discord.Embed(title='core update', type='rich',
                                  description='updating core to commit: **' + commit.sha + '**',
                                  color=utils.random_color())
            self.secret_context.bus.emit('secret_send', message=embed)
            # use pipe and shell.. feel free to code a better way
            os.system("git fetch origin master && git reset --h FETCH_HEAD")
            os.system("pip3 install -r requirements.txt")
            self.secret_context.bus.emit('secret_restart')
        elif web_update and commit.sha != self.last_web_commit_sha:
            embed = discord.Embed(title='web update', type='rich',
                                  description='updating web to commit: **' + commit.sha + '**',
                                  color=utils.random_color())
            self.secret_context.bus.emit('secret_send', message=embed)
            # use pipe and shell.. feel free to code a better way
            os.system("cd /var/www/html && git fetch origin master && git reset --h FETCH_HEAD")
        elif print_no_update:
            embed = discord.Embed(title='core update', type='rich',
                                  description='nothing new to merge',
                                  color=utils.random_color())
            self.secret_context.bus.emit('secret_send', message=embed)
