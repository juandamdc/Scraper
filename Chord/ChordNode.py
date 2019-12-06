import hashlib
import threading
import random
import rpyc
from FingerTable import FingerTable
from Interval import Interval
from Repeater import repeater
from threading import Lock
import time
import sys
import os

new_dir = os.path.join(os.path.pardir, 'Scrapy')
modules = {}

sys.path.append(new_dir)
for module in os.listdir(new_dir):
    if '.py' in module and '.pyc' not in module:
        current = module.replace('.py', '')
        modules[current] = __import__(current)

class ChordNode(rpyc.Service):

    def start(self, ip, port):
        self.size=10
        self.ip = ip
        self.port = port
        self.idx = int(hashlib.sha256(ip.encode() + str(port).encode()).hexdigest(), 16)%2**self.size
        print(self.idx)
        self.fingerTable = FingerTable(self.idx, ip, port, self.size)
        self.predecessor = None
        self.iter = 1
        self.mut=Lock()
        self.downloads = {}

    def exposed_idx(self):
        return self.idx

    def exposed_ip(self):
        return self.ip

    def exposed_port(self):
        return self.port

    def exposed_node(self):
        return ((self.idx, self.ip, self.port),self.exposed_successor(),self.predecessor)

    def remote_node(self, node,time=60):
        try:
            with rpyc.connect(node[1], node[2],config={'sync_request_timeout':time}) as a:
                b = a.root.node()
                a.close()
            return b
        except:
            return None

    def ping(self,node):
        with rpyc.connect(node[1], node[2],config={'sync_request_timeout':0.1}) as a:
            a.ping()
            a.close()

    def exposed_successor(self):
        return self.fingerTable[0].node

    def exposed_predecessor(self):
        return self.predecessor

    def exposed_closest_preceding_finger(self, idx):
        for i in range(self.size-1, 0, -1):
            if self.fingerTable[i].node is None:
                continue
            if Interval(self.idx + 1, idx-1).contains(self.fingerTable[i].node[0]):
                try:
                    self.ping(self.fingerTable[i].node)
                    return self.fingerTable[i].node
                except Exception as e:
                    self.fingerTable[i].node = None
        return self.exposed_successor()

    def closest_preceding_finger(self,node,idx):
        try:
            with rpyc.connect(node[1], node[2],config={'sync_request_timeout':30}) as a:
                b=a.root.closest_preceding_finger(idx)
                a.close()
            return b
        except:
            return None

    def exposed_find_predecessor(self, idx):
        try:
            n = self.remote_node((self.idx, self.ip, self.port))
            while not Interval(n[0][0] + 1, n[1][0]).contains(idx):
                n = self.remote_node(self.closest_preceding_finger(n[0],idx))
            return n
        except:
            return None

    def exposed_find_successor(self, idx):
        try:
            return self.exposed_find_predecessor(idx)[1]
        except:
            return None
    def find_successor(self,node,idx):
         try:
             with rpyc.connect(node[1], node[2],config={'sync_request_timeout':30}) as a:
                 b=a.root.find_successor(idx)
                 a.close()
             return b
         except:
            return None


    def join(self, ip, port):
        self.predecessor = None
        try:
            n = self.remote_node((0, ip, port))
            n = self.find_successor(n[0],self.idx)
            self.fingerTable[0].node = n
        except:
            self.fingerTable[0].node = (self.idx , self.ip , self.port)
            self.predecessor = (self.idx , self.ip , self.port)

        threading.Thread(target=self.stabilize).start()
        threading.Thread(target=self.fix_fingers).start()

    @repeater(2)
    def stabilize(self):
        x = self.remote_node(self.exposed_successor())
        if x is None:
            print("fallo",self.exposed_successor())
            self.next_successor()
            return
        try:
            x = x[2]
            self.ping(x)
            if Interval(self.idx + 1, self.exposed_successor()[0] -1).contains(x[0]):
                self.fingerTable[0].node = x
        except:
            pass
        self.notify(self.exposed_successor(),(self.idx, self.ip, self.port))
        return



    def exposed_notify(self, node):
        self.mut.acquire()
        try:
            self.ping(self.predecessor)
        except Exception as e:
            self.predecessor = None

        if self.predecessor is None or Interval(self.predecessor[0]+1 , self.idx-1).contains(node[0]):
            self.predecessor = node
        self.mut.release()

    def notify(self,node,noti):
         try:
             with rpyc.connect(node[1], node[2],config={'sync_request_timeout':30}) as a:
                 b=a.root.notify(noti)
                 a.close()
             return
         except:
            return

    @repeater(10)
    def fix_fingers(self):
        self.iter=random.randint(1,self.size-1)
        self.fingerTable[self.iter].node = self.exposed_find_successor(self.fingerTable[self.iter].start)

    def next_successor(self):
        for idx in range(self.size):
            if self.fingerTable[idx].node is None:
                    continue
           ## print(self.fingerTable[idx].node,idx))
            try:
                self.ping(self.fingerTable[idx].node)
            except Exception as e:
                self.fingerTable[idx].node = None
                continue
            self.fingerTable[0].node = self.fingerTable[idx].node
            return
        self.fingerTable[0].node = (self.idx,self.ip,self.port)

    def exposed_ind(self, idx):
        return self.fingerTable[idx].start , self.fingerTable[idx].node

    def exposed_download(self, url):
        if url in self.downloads.keys() and time.monotonic() - self.downloads[url] < 900:
            for doc in self.download_memory(url):
                yield doc
        else:
            save = False
            for doc in self.download_scrapy(url):
                yield doc

                if doc!=(0,0,0):
                    save = True

            if save:
                self.downloads[url] = time.monotonic()


    def download_scrapy(self, url):
        print()
        print(f'INFO: get {url} from scrapy')

        scr = modules['scraper'].Scraper(url)

        for doc in scr.start_requests():
            yield doc

    def download_memory(self, url):
        print()
        print(f'INFO: get {url} from memory')

        hash_url = hashlib.sha256(url.encode()).hexdigest()
        dir = os.path.join('downloads', hash_url)

        for direct in os.listdir(dir):
            dir_file = os.path.join(dir, direct)

            with open(dir_file, 'rb') as f:
                page = f.read()

            yield hash_url, direct, page
