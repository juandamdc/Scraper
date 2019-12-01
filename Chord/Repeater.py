import threading

def repeater(sec=1):
    def temp(f):
        def w(*args):
            ticker = threading.Event()
            while not ticker.wait(sec):
                f(*args)
        return w
    return temp
