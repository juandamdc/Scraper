from ChordNode import ChordNode
from  rpyc.utils.helpers import classpartial
from  rpyc.utils.server import ThreadedServer
import threading
import sys


ch2= ChordNode('localhost',int(sys.argv[1]))
t2= ThreadedServer(ch2,port=int(sys.argv[1]))
t2=threading.Thread(target=t2.start)
t2.start()
ch2.join('localhost',8000)
ch2.fingerTable[0]
