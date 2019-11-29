from ChordNode import ChordNode
from  rpyc.utils.helpers import classpartial
from  rpyc.utils.server import ThreadedServer
import threading
import sys

ch2= ChordNode()
ch2.start('192.168.43.83' ,int(sys.argv[1]))
t2= ThreadedServer(ch2,port=int(sys.argv[1]))
t2=threading.Thread(target=t2.start)
t2.start()
ch2.join('192.168.43.252',8000)
print(ch2.fingerTable[0].node)
print(ch2.exposed_predecessor())
