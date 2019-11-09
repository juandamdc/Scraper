import hashlib
import threading
import rpyc
import threading

from rpyc.utils.server import ThreadedServer

from FingerTable import FingerTable
from Interval import Interval
from Repeater import repeater


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

    def node(self):
        return self.idx, self.ip, self.port


    def remote_node(self, node):
    	return rpyc.connect(node[1],node[2]).root
      
    def exposed_successor(self):
        return self.fingerTable[0].node[0], self.fingerTable[0].node[1] , self.fingerTable[0].node[2]

    def exposed_predecessor(self):
        return self.predecessor

    def exposed_closest_preceding_finger(self, idx):
        for i in range(255, 0, -1):
            if self.fingerTable[i].node is None:
                continue
            if Interval(self.idx + 1, idx - 1).contains(self.fingerTable[i].node[0]):
                try:
                    return self.fingerTable[i].node
                except Exception:
                    self.fingerTable[i].node = None
        return self.exposed_successor()

    def exposed_find_predecessor(self, idx):
        n = self.remote_node((self.idx, self.ip, self.port))
        while not Interval(n.idx() + 1, n.successor()[0]).contains(idx):
            n = self.remote_node(n.closest_preceding_finger(idx))
        return n.idx(),n.ip(),n.port()

    def exposed_find_successor(self, idx):
        n = self.remote_node(self.exposed_find_predecessor(idx)).successor()
        return n

    def join(self, ip, port):
        self.predecessor = None
        try:
            n = self.remote_node((0, ip, port))
            print(n.idx())
            n = n.find_successor(self.idx)
            self.fingerTable[0].node = n
        except Exception as e:
            print(e)
            self.fingerTable[0].node = self.node()
            self.predecessor=self.node()

        threading.Thread(target=self.stabilize).start()
        threading.Thread(target=self.fix_fingers).start()
        


    @repeater(2)
    def stabilize(self):
        print("start-stabilize")
        x = self.remote_node(self.exposed_successor())
        try:
            x = self.remote_node(x.predecessor())
        except Exception as e:
            return

        if Interval(self.idx + 1, self.exposed_successor()[0] - 1).contains(x.idx()):
            self.fingerTable[0].node = (x.idx(),x.ip(),x.port())
        self.remote_node(self.exposed_successor()).notify((self.idx,self.ip,self.port))
        print("end-stabilize")

    def exposed_notify(self, node):
        if self.predecessor is None or Interval(self.predecessor[0] + 1, self.idx - 1).contains(node[0]):
            self.predecessor = node

    @repeater(10)
    def fix_fingers(self):
        self.fingerTable[self.iter].node = self.exposed_find_successor(self.fingerTable[self.iter].start)
        self.iter += 1
        if self.iter == 256:
            self.iter = 1





