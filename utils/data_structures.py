from collections import deque

class FixedSizePairList:
    def __init__(self, size):
        self.size = size
        self.data = deque(maxlen=size)

    def add(self, element):
        if isinstance(element, tuple) and len(element) == 2:
            self.data.append(element)
        else:
            raise ValueError("Element must be a tuple with two items")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __repr__(self):
        return list(self.data).__repr__()
