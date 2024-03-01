""" 
=======
Company
=======
@file: Company.py
@author: Bin Liang
@date: 2023-2-29

"""




class Company:
    
    def __init__(self, config):
        raise NotImplementedError


    def __call__(self, *args, **kwds):
        raise NotImplementedError
    
    def working(self, task:str) -> None:
        raise NotImplementedError
    
    
    def save(self) -> None:
        raise NotImplementedError
    
    
    