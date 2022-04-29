from collections import deque


class Storage:

    def __init__(self):
        self.queue = deque()

    def push(self, message):
        self.queue.append(message)

    def pop(self):
        return self.queue.popleft()

    def size(self):
        return len(self.queue)
