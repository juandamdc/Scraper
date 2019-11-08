from Chord.ChordNode import ChordNode
from  rpyc.utils.helpers import classpartial
from  rpyc.utils.server import ThreadedServer

ch= ChordNode('localhost',8000)
t= ThreadedServer(ch,8000)
t.start()

