"""
================
ManagerAssistant
================
@file_name: manager_assistant.py
@author: Bin Liang
@date: 2024-04-09
"""

__all__ = ["ManagerAssistant"]

from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent
from xyz.utils.llm.openai_client import OpenAIClient


class ManagerAssistant(Agent):
    information: str
    llm_prompt_engineer: LLMAgent

    def __init__(self, core_agent: OpenAIClient) -> None:
        """
        The manager assistant is a class for manager task assignment and execution supervision.

        Parameters
        ----------
        core_agent: OpenAIClient
            The core agent of the AutoPromptEngineer.


        """
        super().__init__()

        # Set the information of the assistant. The information is used to help the user understand the assistant.
        self.set_information({
            "type": "function",
            "function": {
                "name": "ManagerAssistant",
                "description": "Manager can make a plan for the task which contain task assignment and execution "
                               "supervision.",
                "parameters": {"task": {"type": "str", "description": "The task which the user want to do."},
                               "source": {"type": "list", "description": "The Agents in this company."},
                               },
                "required": ["task"],
            },
        })

        # Using the template we designed to define the assistant, which can do the main task.
        self.llm_prompt_engineer = LLMAgent(template=manager_prompt, core_agent=core_agent, stream=False)

    def flowing(self, task: str, ) -> str:
        """
        The main function of the ManagerAssistant.

        Parameters
        ----------
        task: str
            The task which the user want to do.

        Returns
        -------
        str
            The prompts of the AutoPromptEngineer.
        """

        return self.llm_prompt_engineer(task=task)


manager_prompt = [
    {"role": "system", "content": """

"""
     },

    {"role": "user", "content": """

"""
     }
]
