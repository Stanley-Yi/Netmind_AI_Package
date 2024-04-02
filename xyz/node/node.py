"""
====
Node
====
@file_name: node.py
@author: Bin Liang
@date: 2024-3-15

"""


__all__ = ["Node"]

from abc import abstractmethod
from typing import Callable, Any


class Node:
    type: str

    def __init__(self):

        super().__setattr__("type", "node")

    def _wrap_call(self, **kwargs) -> Callable:

        return self.flowing(**kwargs)

    __call__: Callable[..., Any] = _wrap_call

    @abstractmethod
    def flowing(self, *args, **kwargs) -> Any:
        """
        We can use the overload for multimodal
        """
        ...
