import sys

from .. import settings

def debug(*args):
    if settings.DEBUG:
        print("[DEBUG] {}: ".format(sys._getframe(1).f_code.co_name) + " ".join(map(str, args)))
    else:
        pass