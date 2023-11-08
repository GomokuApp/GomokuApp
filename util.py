from time import time


class Player:
    ip: int
    last_checkin: float

    def __init__(self, ip):
        self.ip = ip
        self.refresh()

    def refresh(self):
        self.last_checkin = time()
