import hashlib
import threading
import rpyc

from rpyc.utils.server import ThreadedServer

from Chord.FingerTable import FingerTable, Node
from Chord.Interval import Interval
from Chord.Repeater import repeater


class ChordNode(rpyc.Service):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.idx = int(hashlib.sha256(ip.encode() + str(port).encode()).hexdigest(), 16)
        self.fingerTable = FingerTable(self.idx, ip, port, 256)
        self.predecessor = None
        self.iter = 1

    def exposed_idx(self):
        return self.idx

    def exposed_ip(self):
        return self.ip

    def exposed_port(self):
        return self.port

    def exposed_node(self):
        return Node(self.idx, self.ip, self.port)

    def remote_node(self, node):
        return rpyc.connect(node.ip, node.port).root

    def exposed_successor(self):
        return self.remote_node(self.fingerTable[0].node)

    def exposed_predecessor(self):
        return self.remote_node(self.predecessor)

    def exposed_closest_preceding_finger(self, idx):
        for i in range(255, 0, -1):
            if self.fingerTable[i].node is None:
                continue
            if Interval(self.idx + 1, idx - 1).contains(self.fingerTable[i].node.idx):
                try:
                    return self.remote_node(self.fingerTable[i].node)
                except Exception:
                    self.fingerTable[i].node = None
        return self.exposed_successor()

    def exposed_find_predecessor(self, idx):
        n = self.remote_node(Node(self.idx, self.ip, self.port))
        while not Interval(n.idx() + 1, n.successor().idx()).contains(idx):
            n = n.closest_preceding_finger(idx)
        return n

    def exposed_find_successor(self, idx):
        n = self.exposed_find_predecessor(idx)
        return n.successor()

    def join(self, ip, port):
        self.predecessor = None
        try:
            n = self.remote_node(Node(0, ip, port)).find_successor(self.idx)
            self.fingerTable[0].node = n.node()
        except:
            self.fingerTable[0].node = self.exposed_node()
        self.stabilize()
        self.fix_fingers()


    @repeater
    def stabilize(self):
        x = self.exposed_successor().predecessor()
        if Interval(self.idx + 1, self.exposed_successor().idx() - 1).contains(x.idx()):
            self.fingerTable[0].node = x.node()
        self.exposed_successor().notify(self.exposed_node())

    def exposed_notify(self, node):
        if self.predecessor is None or Interval(self.predecessor.idx + 1, self.idx - 1).contains(node.idx):
            self.predecessor = node

    @repeater
    def fix_fingers(self):
        self.fingerTable[self.iter] = self.exposed_find_successor(self.fingerTable[self.iter].start)
        self.iter += 1
        if self.iter == 256:
            self.iter = 1



a = ChordNode("localhost", 8000)
a.join(None,None)
t= ThreadedServer(a,port=8000)
h=threading.Thread(target=t.start)
h.start()
print(a.exposed_find_successor(10).idx())
print(a.exposed_find_successor(10).idx())


