import time


class Timer:
    timers: dict[str, float] = {}

    def __init__(self):
        self.start_time = time.time()

    def start(self, name: str):
        self.timers[name] = time.time()

    def stop(self, name: str):
        self.timers[name] = time.time() - self.timers[name]

    def get(self, name: str) -> float:
        return self.timers[name]

    def __getitem__(self, name: str) -> float:
        return self.timers[name]

    def __setitem__(self, name: str, value: float) -> None:
        self.timers[name] = value


timer = Timer()
