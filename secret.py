import time

from threading import Thread


class SecRet(Thread):
    def __init__(self):
        Thread.__init__(self)

        # setup github

    def run(self):
        while True:
            # TODO: auto update
            time.sleep(60 * 15)
