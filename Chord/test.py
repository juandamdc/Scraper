from ChordNode import ChordNode
from  rpyc.utils.helpers import classpartial
from  rpyc.utils.server import ThreadedServer
import threading
import sys

ch= ChordNode()
ch.start('192.168.43.83' ,8000)
t= ThreadedServer(ch,port=8000)
t=threading.Thread(target=t.start)
t.start()
ch.join(None,None)

#ch2= ChordNode('localhost',8001)
#t2= ThreadedServer(ch2,port=8001)
#t2=threading.Thread(target=t2.start)
#t2.start()
#ch2.join('localhost',8000)
#ch2.fingerTable[0]

print(1)