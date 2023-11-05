from time import time

class Player:
    def __init__(self, ip):
        self.ip = ip
        self.refresh()

    def refresh(self):
        self.last_checkin = time()