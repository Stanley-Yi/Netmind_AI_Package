from enum import Enum

class IdxType(Enum):
    FLAT = 1
    IVF_FLAT = 2
    GPU_IVF_FLAT = 3
    IVF_SQ8 = 4
    IVF_PQ = 5
    GPU_IVF_PQ = 6
    HNSW = 7
    SCANN = 8
    BIN_FLAT = 9
    BIN_IVF_FLAT = 10
    
    
    
    def __str__(self):
        return str(self.name)