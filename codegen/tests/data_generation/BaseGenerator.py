import random


class BaseGenerator:
    def __init__(self, seed: int = 0):
        self.random = random.Random(seed)
        pass

    def generate(self):
        return self.random.random()


