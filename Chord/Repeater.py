import threading , time


def repeater(sec=1):
    def temp(f):
        def w(*args):
            while 1:
            	time.sleep(sec)
            	try:
            		f(*args)
            	except Exception as e:
            		pass  
        return w
    return temp