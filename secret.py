import time

import os

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

        Thread.__init__(self)

    def run(self):
        # sleep until 00
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
        self.ding()
        self.auto_update()

    def ding(self):
        now = datetime.now()
        s = ''
        for i in range(0, now.hour):
            s += 'DING '
        self.bus.emit('secret_send', message=s)

    def auto_update(self):
        commits = self.git_repo.get_commits()
        commit = commits[0]
        if commit.sha != self.last_commit_sha:
            self.bus.emit('secret_send', message='**updating secRet sources**')
            while commit.sha != self.last_commit_sha:
                self.bus.emit('secret_send', message='**merging:**' + ' ' + commit.commit.message +
                                                     '\n**from** ' + commit.author.name)
            # use pipe and shell.. feel free to code a better way
            os.system("git fetch origin master")
            os.system("git reset --h FETCH_HEAD")
            self.bus.emit('secret_restart')



