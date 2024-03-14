""" 
====
Edge
====
@file_name: Edge.py
@author: Bin Liang
@date: 2024-03-13
We use this object which can connect two nodes. And we can make the output of one node as the input of another node.
"""


from xyz.node.CoreAgent import CoreAgent


class Edge:
    
    
    def __init__(self, front_node, back_node) -> None:
        
        self.front_node = front_node
        self.back_node = back_node
        
    def bridge(self, input):
        
        parameters = self.back_node.format_input(input)
        
        return parameters
        
    def info(self):
        
        return {
            "front_node": self.front_node.name,
            "back_node": self.back_node.name
        }
