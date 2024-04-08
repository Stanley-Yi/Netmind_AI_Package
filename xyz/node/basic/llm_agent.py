""" 
========
LLMAgent
========
@file_name: llm_agent.py
@author: Bin Liang
@date: 2023-2-29

"""

from copy import deepcopy
from typing import Generator, List, Any

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient

__all__ = ["LLMAgent"]


class LLMAgent(Agent):
    """ 
    An assistant that uses the LLM (Language Learning Model) for processing messages.
    """

    def __init__(self, template: list, core_agent: OpenAIClient, stream: bool = False) -> None:
        """
        Initialize the LLMAgent.

        Parameters
        ----------
        template: list
            The template for the assistant's prompts. It should be a list of OpenAI's messages.
        core_agent: OpenAIClient
            The core agent for the assistant.
        stream: bool, optional
            Whether to stream the assistant's messages, by default False.
        """
        super().__init__()

        self.core_agent = core_agent

        generate_parameters = {"stream": stream}
        self.node_config = {"template": template,
                            "generate_parameters": generate_parameters}

        self.template = self.node_config['template']
        self.generate_parameters = self.node_config['generate_parameters']
        self.last_request_info = {}

    def flowing(self, messages: list = None, tools: list = None, **kwargs) -> str:
        """When you call this assistant, we will run the assistant with the given keyword arguments from the prompts.
        Before we call the OpenAI's API, we do some interface on this message.

        Parameters

        """

        if messages is None:
            local_messages = []
        else:
            local_messages = deepcopy(messages)
            messages = None  # This is necessary, because we need to reset the messages

        if tools is None:
            local_tools = []
        else:
            local_tools = deepcopy(tools)
            tools = None

        system_message, current_message = self._complete_prompts(**kwargs)

        local_messages.extend(current_message)
        return self.request(messages=local_messages, tools=local_tools)

    def request(self, messages: list, tools: list = None) -> Any:
        """
        Run the assistant with the given keyword arguments.
        """

        if tools is None:
            tools = []
        self.last_request_info = {
            "messages": messages,
            "tools": tools
        }

        if self.generate_parameters["stream"]:
            return self._stream_run(messages)
        else:
            response = self.core_agent.run(messages=messages, tools=tools)
            content = response.choices[0].message.content

            # TODO: 要检测出是否一定有 tool 的返回
            if content is None:
                return response.choices[0].message.tool_calls[0].function
            else:
                return content

    def _stream_run(self, messages: list) -> Generator[str, None, None]:
        """
        Run the assistant in a streaming manner with the given messages.
        """

        return self.core_agent.stream_run(messages)

    def debug(self) -> dict[Any, Any]:
        """
        Reset the assistant's messages.

        Returns
        -------
        dict
            The last time the request messages and tools.
        """

        return self.last_request_info

    def _complete_prompts(self, **kwargs) -> tuple:  # TODO: 这里的返回值不够明确
        """
        Complete the assistant's prompts with the given keyword arguments.

        Parameters
        ----------
        **kwargs
            The keyword arguments to use for completing the prompts.

        Returns
        -------
        tuple
            A tuple containing the system message and the user message.
        """

        if type(self.template) is list:

            current_messages = deepcopy(self.template)
            system_message = {}

            for i in range(len(current_messages)):
                current_messages[i]['content'] = current_messages[i]['content'].format(**kwargs)
                if current_messages[i]['role'] == 'system':
                    system_message = current_messages[i]

            return system_message, current_messages
