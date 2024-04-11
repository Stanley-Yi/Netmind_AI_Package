"""
=====
Graph
=====
@file_name: agent_graph.py
@author: Bin Liang
@date: 2024-04-09
"""


__all__ = ["AgentGraph"]


class AgentGraph:
    """
    The AgentGraph is a class for graph.
    """

    def __init__(self) -> None:
        self.Node = {}
        self.Edge = {}

    def add_nodes(self) -> None:
        raise NotImplementedError

    def delete_nodes(self) -> None:
        raise NotImplementedError

    def get_nodes(self) -> None:
        raise NotImplementedError

