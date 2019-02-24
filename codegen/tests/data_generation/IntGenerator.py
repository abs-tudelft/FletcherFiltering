import random


class IntGenerator:
    def __init__(self, seed: int = 0):
        self.random = random.Random(seed)
        pass

    def generate(self, size: int = 32):
        return self.random.randint(-(2 ** (size-1)), 2 ** (size - 1) - 1)


