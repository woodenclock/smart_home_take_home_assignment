from datetime import datetime


class SystemClock:
    def now(self):
        return datetime.now()


class FakeClock:
    def __init__(self, fixed_datetime):
        self.fixed_datetime = fixed_datetime

    def now(self):
        return self.fixed_datetime