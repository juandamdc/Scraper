from Chord.Interval import Interval


class FingerTable:
    def __init__(self, id, ip, port, size):
        self.id = id
        self.size = size
        self.table = [TableEntry(None, (2 ** j + id) % 2 ** size, (2 ** (j + 1) + id) % 2 ** size, None, None) for j in
                      range(size)]

    def __getitem__(self, item):
        return self.table[item]

    def __setitem__(self, key, value):
        self.table[key] = value


class TableEntry:
    def __init__(self, idx, start, end, ip=0, port=0):
        self.start = start
        self.interval = Interval(start, end)
        self.node =Node(idx, ip, port)
        if idx is None:
            self.node=None

class Node:
    def __init__(self, idx, ip, port):
        self.idx = idx
        self.ip = ip
        self.port = port
