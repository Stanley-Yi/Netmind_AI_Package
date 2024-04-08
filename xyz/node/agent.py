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
    output: dict

    def __init__(self):
        """
        The basic class of agent.
        User can create a new agent by inheriting this class.

        Examples
        --------
        >>> class MyAgent(Agent):
        >>>     def __init__(self):
        >>>         super().__init__()
        >>>         self.set_information({
        >>>             "type": "function",
        >>>             "function": {
        >>>                 "name": "MyAgent",
        >>>                 "description": "This is a test agent.",
        >>>                 "parameters": {"a": {"type": "int", "description": "The first parameter."},
        >>>                                "b": {"type": "int", "description": "The second parameter."}
        >>>                                },
        >>>                 "required": ["a", "b"],
        >>>             },
        >>>         })
        >>>    def flowing(self, a: int, b: int) -> int:
        >>>        return a + b

        1. The user can create a new agent by inheriting this class.
        2. The user must set the information by call the method `set_information`. The format of the information is
        following the OpenAI's function call format. ref: https://platform.openai.com/docs/guides/function-calling
        3. The user must implement the method `flowing`. The method `flowing` is the main function of the agent.
        """

        super().__setattr__("type", "agent")
        super().__setattr__("information", dict)
        super().__setattr__("output", dict)

    def _wrap_call(self, **kwargs) -> Callable:
        """
        The wrap call function for the agent. The user can call the agent by `agent(**kwargs)`.
        The agent will call the method `flowing` automatically.

        Parameters
        ----------
            **kwargs:

        Returns
        -------
            self.flowing(**kwargs)
        """

        return self.flowing(**kwargs)

    __call__: Callable[..., Any] = _wrap_call

    @abstractmethod
    def flowing(self, *args, **kwargs) -> Any:
        """
        The main function of the agent. The user must implement this function.
        """
        ...

    def set_information(self, information: dict) -> None:
        """
        Set the information of the agent. And check the format of the information.

        Parameters
        ----------
            information: dict
                The information of the agent. The format of the information is following the OpenAI's function call
                format.

        Returns
        -------
            None
        """

        assert type(information) is dict, "The information must be a dict."
        assert "type" in information, "The information must have a key 'name'."
        assert "function" in information, "The information must have a key 'function'."
        assert "name" in information["function"], "The information must have a key 'name'."
        assert "description" in information["function"], "The information must have a key 'description'."
        assert "parameters" in information["function"], "The information must have a key 'parameters'."
        assert "required" in information["function"], "The information must have a key 'required'."

        self.information = information

    # ======= 以下是为了方便查看 multi-agents-system 的结果的。可删。
    def __str__(self) -> str:
        """
        The string format of the agent.

        Returns
        -------
            str
        """

        info = (f"Agent(name={self.information['name']}, description={self.information['description']}, "
                f"parameters={self.information['parameters']})")

        for key, value in vars(self).items():
            try:
                if "type" in vars(value) and value.type == "assistant":
                    info += f"\n\n\t[SubAgent: {key}: {value._structure(2)}]"
            except:
                pass

        return info

    def _structure(self, order: int) -> str:
        """
        The structure of the agent.

        Parameters
        ----------
        order: int
            Level of the current Agent in the system.

        Returns
        -------
            str
                The structure format of the agent.
        """

        pre_blank = "\t" * order
        info = (f"{pre_blank}Agent(name={self.information['name']}, description={self.information['description']}, "
                f"parameters={self.information['parameters']})")

        for key, value in vars(self).items():
            try:
                if "type" in vars(value) and value.type == "agent":
                    info += f"\n{pre_blank}[SubAgent: {key}: {value._structure(order + 1)}]"
            except:
                pass

        return info
