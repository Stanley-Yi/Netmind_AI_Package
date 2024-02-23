from enum import Enum

class FilterOperand(Enum):
    LESS_THAN = '<'
    GREATER_THAN = '>'
    EQUAL_TO = '=='
    NOT_EQUAL_TO = '!='
    GREATER_OR_EQUAL = '>='
    LESS_OR_EQUAL = '<='
    LIKE = 'like'
    
    
    def __str__(self):
        return str(self.name)
