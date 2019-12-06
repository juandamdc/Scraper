from  rpyc.utils.helpers import classpartial
from  rpyc.utils.server import ThreadedServer
import threading
import sys
import os

new_dir = os.path.join(os.path.pardir, 'Chord')
modules = {}

sys.path.append(new_dir)
for module in os.listdir(new_dir):
    if '.py' in module and '.pyc' not in module:
        current = module.replace('.py', '')
        modules[current] = __import__(current)

ch= modules['ChordNode'].ChordNode()
ch.start(sys.argv[1], int(sys.argv[2]))
t= ThreadedServer(ch,port=int(sys.argv[2]))
t=threading.Thread(target=t.start)
t.start()
ch.join(sys.argv[3], sys.argv[4])
