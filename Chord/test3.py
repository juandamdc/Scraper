from ChordNode import ChordNode
from  rpyc.utils.helpers import classpartial
from  rpyc.utils.server import ThreadedServer
import threading
import sys
import time
from multiprocessing import Process


for i in range(200,300):
	print('------------------------',i,'---------------------')
	ch2= ChordNode()
	ch2.start('127.0.0.1' ,8001+i)
	t2 = ThreadedServer(ch2,port=int(8001+i))
	t2=threading.Thread(target=t2.start)
	t2.start()
	ch2.join('127.0.0.1',8000)