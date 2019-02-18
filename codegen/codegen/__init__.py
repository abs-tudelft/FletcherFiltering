DEBUG = False

def debug(*args):
    if DEBUG:
        print("[DEBUG] {}: ".format(sys._getframe(1).f_code.co_name) + " ".join(map(str, args)))
    else:
        pass