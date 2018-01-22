import time

from datetime import datetime
from threading import Thread


class SecRet(Thread):
    def __init__(self, bus):
        self.bus = bus
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

    def ding(self):
        now = datetime.now()
        s = ''
        for i in range(0, now.hour):
            s += 'DING '
        self.bus.emit('secret_send', message=s)
