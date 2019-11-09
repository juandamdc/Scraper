from ChordNode import ChordNode
from  rpyc.utils.helpers import classpartial
from  rpyc.utils.server import ThreadedServer
import threading



ch2= ChordNode('localhost',8003)
t2= ThreadedServer(ch2,port=8003)
t2=threading.Thread(target=t2.start)
t2.start()
ch2.join('localhost',8000)
ch2.fingerTable[0]
