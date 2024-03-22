"""
=========
CoreAGent
=========
@file_name: core_agent.py
@author: Netmind.AI BlackSheep team
@date: 2024-1-10
To define the BlackSheep-Agent(The BasicCLass of Agent)
"""


from typing import Generator, overload

from xyz.utils.llm.core_agent import CoreAgent


class DummyLLM(CoreAgent):

    def __init__(self):
        super().__setattr__("name", "DummyLLM")
        super().__setattr__("description", "You can not get response in this class.")

    def run(self, messages: list, tools=[]) -> str:

        raise TypeError("You do not set a llm-agent in this progress. Please ser a llm-agent first.")

        return None

    def stream_run(self, messages: list) -> Generator[str, None, None]:

        raise TypeError("You do not set a llm-agent in this progress. Please ser a llm-agent first.")

        yield None


dummy_agent = DummyLLM()