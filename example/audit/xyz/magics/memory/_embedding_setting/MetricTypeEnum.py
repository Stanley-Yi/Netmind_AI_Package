from enum import Enum

class MetricType(Enum):
    L2 = 1
    IP = 2
    COSINE = 3
    JACCARD = 4
    HAMMING = 5
    
    
    def __str__(self):
        return str(self.name)
