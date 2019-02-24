import random


class UIntGenerator:
    def __init__(self, seed: int = 0):
        self.random = random.Random(seed)
        pass

    def generate(self, size: int = 32):
        return self.random.randint(0, 2 ** size - 1)


