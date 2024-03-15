""" 
========
ABSAgent
========
@file_name: ABSAgent.py
@author: Bin Liang
@date: 2024-3-1

"""


# python standard packages
from abc import ABC, abstractmethod
from typing import Any

# python third-party packages

# python first-party packages


class ABSAgent(ABC):

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.request(*args, **kwargs)

    @abstractmethod
    def request(self, *args: Any, **kwargs: Any) -> Any:
        """All the agents should have a request method to process the messages.

        Parameters
        ----------
        input : Any
            The input to be processed.

        Returns
        -------
        Any
            The response from the agent.
        """
        pass
    
    