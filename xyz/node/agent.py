"""
====
Node
====
@file_name: agent.py
@author: Bin Liang
@date: 2024-3-15

"""


from typing import Dict, Callable, Any
from abc import abstractmethod

from xyz.node.operation.InputFormatAgent import InputFormatAgent
from xyz.parameters import core_agent as default_agent

__all__ = ["Agent"]


class Agent:

    name : str
    description : str
    input_format_agent : InputFormatAgent
    template : str

    def __init__(self, core_agent=default_agent) -> None:
        # TODO: Careful with this. You'd better use super().__init__(core_agent)
        self.input_format_agent = InputFormatAgent(core_agent)
        self.core_agent = core_agent

        super().__setattr__("name", "")
        super().__setattr__("description", "")

    def _wrap_call(self, *args, **kwargs) -> Callable :
        # TODO: Preparing for hooks part. For example, we can add a hook to see the process.
        return self.flowing(*args, **kwargs)

    __call__ : Callable[..., Any] = _wrap_call

    @abstractmethod
    def flowing(self, *args, **kwargs) -> ...:
        """
        We can use the overload for multimodal
        """
        ...

    @abstractmethod
    def tools_format(self) -> Dict[str, str]:
        pass

    @property
    def as_tool(self) -> Dict[str, str]:
        return self.tools_format()

