import queue
import threading


class Channel:
    def __init__(self):
        self.queue = queue.Queue()
    
    def send(self, *values):
        self.queue.put(values)
    
    def receive(self, count=1):
        values = self.queue.get(block=True)
        if count == 1:
            return values[0] if len(values) == 1 else values
        return values[:count]
    
    def is_empty(self):
        return self.queue.empty()
