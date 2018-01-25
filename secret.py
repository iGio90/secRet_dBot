import time

import os

import discord

import utils
from commands import commands_git
from datetime import datetime
from threading import Thread


class SecRet(Thread):
    def __init__(self, bus, git_repo):
        # event bus
        self.bus = bus
        # git repo
        self.git_repo = git_repo
        # get and hold last commit sha for auto update
        self.last_commit_sha = commands_git.get_last_commit(git_repo).sha

        # register bus event
        self.bus.add_event(self.secret_update, 'secret_update')

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
        self.bus.emit('secret_ping')

        # check for update through git
        self.secret_update()

    def secret_update(self, print_no_update=False):
        commits = self.git_repo.get_commits()
        commit = commits[0]
        if commit.sha != self.last_commit_sha:
            embed = discord.Embed(title='core update', type='rich',
                                  description='updating core to commit: **' + commit.sha + '**',
                                  color=utils.random_color())
            self.bus.emit('secret_send', message=embed)
            # use pipe and shell.. feel free to code a better way
            os.system("git fetch origin master")
            os.system("git reset --h FETCH_HEAD")
            # it does actually throw segmentation fault O.O
            # os.system("pip3 install -r requirements.txt")
            self.bus.emit('secret_restart')
        elif print_no_update:
            embed = discord.Embed(title='core update', type='rich',
                                  description='nothing new to merge',
                                  color=utils.random_color())
            self.bus.emit('secret_send', message=embed)



