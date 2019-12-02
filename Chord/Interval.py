class Interval:

    def __init__(self, a, b):
        self.down = a
        self.up = b

    def contains(self, a):
        if self.up > self.down:
            return a >= self.down and a < self.up
        else:
            return a >= self.down or a < self.up
