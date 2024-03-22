""" 
====
Edge
====
@file_name: edge.py
@author: Bin Liang
@date: 2024-03-13
We use this object which can connect two nodes. And we can make the output of one node as the input of another node.
"""


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
        
    def format_input(self, input: str) -> Dict[str, str]:
        """
        Format the input for the node.

        Parameters
        ----------
        input : str
            The input to format.

        Returns
        -------
        dict
            The formatted input.
        """

        tools = [self.as_tool]
        _, parameters = self.input_format_agent(tools=tools, input=input)

        return parameters
