"""
====
Node
====
@file_name: node.py
@author: Bin Liang
@date: 2024-3-15
"""


__all__ = ["Agent"]

from abc import abstractmethod
from typing import Callable, Any


class Agent:
    type: str
    information: dict

    def __init__(self):

        super().__setattr__("type", "agent")
        super().__setattr__("information", dict)

    def _wrap_call(self, **kwargs) -> Callable:

        return self.flowing(**kwargs)

    __call__: Callable[..., Any] = _wrap_call

    @abstractmethod
    def flowing(self, *args, **kwargs) -> Any:
        """
        We can use the overload for multimodal
        """
        ...

    def set_information(self, information: dict) -> None:

        self.information = information

    # ======= 以下是为了方便查看 multi-agents-system 的结果的。可删。
    def __str__(self) -> str:

        info = (f"Agent(name={self.information['name']}, description={self.information['description']}, "
                f"parameters={self.information['parameters']})")

        for key, value in vars(self).items():
            try:
                if "type" in vars(value) and value.type == "assistant":
                    info += f"\n\n\t[SubAgent: {key}: {value._structure(2)}]"
            except:
                pass

        return info

    def _structure(self, order) -> str:

        pre_blank = "\t"*order
        info = (f"{pre_blank}Agent(name={self.information['name']}, description={self.information['description']}, "
                f"parameters={self.information['parameters']})")

        for key, value in vars(self).items():
            try:
                if "type" in vars(value) and value.type == "agent":
                    info += f"\n{pre_blank}[SubAgent: {key}: {value._structure(order+1)}]"
            except:
                pass

        return info


