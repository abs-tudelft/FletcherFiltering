import random


class FloatGenerator:
    ieee_floats = {
        16: {'exp': 5, 'significand': 11, 'digits': 3.31},
        32: {'exp': 8, 'significand': 24, 'digits': 7.22},
        64: {'exp': 11, 'significand': 53, 'digits': 15.95},
        128: {'exp': 15, 'significand': 113, 'digits': 34.02}
    }

    def __init__(self, seed: int = 0):
        self.random = random.Random(seed)
        pass

    def generate(self, size: int = 32):
        b = 2
        q = size
        if size in self.ieee_floats:
            emax = 2 ** (self.ieee_floats[size]['exp'] - 1) - 1
            emin = 1 - emax
            p = self.ieee_floats[size]['significand']
            return self.random.uniform(-2 ** (emin+1), 2 ** emax)
        else:
            raise ValueError("Size {} is not valid for IEEE floats.".format(size))
