""" 
====
Edge
====
@file_name: edge.py
@author: Bin Liang
@date: 2024-03-13
We use this object which can connect two nodes. And we can make the output of one node as the input of another node.
"""

from typing import Dict


class Edge:

    def __init__(self, front_node, back_node, input_format_agent) -> None:
        self.front_node = front_node
        self.back_node = back_node
        self.input_format_agent = input_format_agent

        self.front_node.add_input_format_agent(self.input_format_agent)
        self.back_node.add_input_format_agent(self.input_format_agent)

    def bridge(self, input):

        parameters = self.back_node.format_input(input)

        return parameters

    def info(self):
        return {
            "front_node": self.front_node.name,
            "back_node": self.back_node.name
        }
