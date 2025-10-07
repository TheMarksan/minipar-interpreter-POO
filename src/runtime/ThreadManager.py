import threading
import time


class ThreadManager:
    def __init__(self):
        self.threads = []
        self.lock = threading.Lock()
    
    def create_thread(self, target, args=()):
        thread = threading.Thread(target=target, args=args)
        with self.lock:
            self.threads.append(thread)
        return thread
    
    def start_all(self):
        threads_copy = None
        with self.lock:
            threads_copy = self.threads.copy()
        
        for thread in threads_copy:
            thread.start()
    
    def join_all(self):
        threads_copy = None
        with self.lock:
            threads_copy = self.threads.copy()
        
        for thread in threads_copy:
            if thread.is_alive():
                thread.join()
    
    def clear(self):
        with self.lock:
            self.threads.clear()
