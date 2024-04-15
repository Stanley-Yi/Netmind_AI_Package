""" 
========
LLMAgent
========
@file_name: llm_agent.py
@author: Bin Liang
@date: 2023-2-29

"""

from copy import deepcopy
from typing import Generator, Any

from xyz.node.agent import Agent
from xyz.utils.llm.openai_client import OpenAIClient

__all__ = ["LLMAgent"]


class LLMAgent(Agent):
    """ 
    An assistant that uses the LLM (Language Learning Model) for processing messages.

    1， This agent will have a template for the assistant's prompts.
    2， This agent will have a core agent for calling the OpenAI API.
    3， This agent will have a stream parameter for streaming the assistant's messages.
    """
    information: dict
    llm_client: OpenAIClient
    last_request_info: dict
    node_config: dict
    template: list
    generate_parameters: dict


    def __init__(self, template: list, core_agent: OpenAIClient, stream: bool = False, multi_choice: bool = False) -> None:
        """
        Initialize the assistant with the given template and core agent.

        Parameters
        ----------
        template: list
            The template for the assistant's prompts. It should be a list of OpenAI's messages.
        llm_client: OpenAIClient
            The core agent for the assistant.
        stream: bool, optional
            Whether to stream the assistant's messages, by default False.

        Examples
        --------
        >>> from xyz.utils.llm.openai_client import OpenAIClient
        >>> from xyz.elements.assistant.llm_agent import LLMAgent
        >>> core_agent = OpenAIClient()
        >>> template = [{"role": "system", "content": "Now you are a story writer. Please write a story for user."},
        >>>             {"role": "user", "content": "{content}"}]
        >>> assistant = LLMAgent(template=template, core_agent=llm_client, stream=False)
        >>> output = assistant(content="I want to write a story about a dog.")
        """
        super().__init__()

        self.llm_client = llm_client

        # The node_config is used to store the assistant's configuration.
        self.template = template
        self.stream = stream
        self.multi_choice = multi_choice

        self.last_request_info = {}

    def flowing(self, messages: list = None, tools: list = None, images: list = None, **kwargs) -> Any:
        """When you call this assistant, we will run the assistant with the given keyword arguments from the prompts.
        Before we call the OpenAI's API, we do some interface on this message.

        Parameters
        ----------
        messages: list, optional
            The messages to use for completing the prompts, by default None.
        tools: list, optional
            The tools to use for completing the prompts, by default None.
        **kwargs
            The keyword arguments to use for completing the prompts.

        Returns
        -------
        str/generator
            The response from the assistant. If stream == True, we will return a generator.
        """

        local_messages, messages = self._reset_default_list(messages)
        local_tools, tools = self._reset_default_list(tools)
        local_messages.extend(self._complete_prompts(**kwargs))

        return self.request(messages=local_messages, tools=local_tools, images=images)

    def request(self, messages: list, tools: list, images: list) -> Any:
        """
        Run the assistant with the given keyword arguments.
        """

        self.last_request_info = {
            "messages": messages,
            "tools": tools,
            "images": images
        }

        if self.stream:
            return self._stream_run(messages=messages, images=images)
        else:
            response = self.llm_client.run(messages=messages, tools=tools, images=images)
            if self.multi_choice:
                return response
            
            content = response.choices[0].message.content

            # TODO: 要检测出是否一定有 tool 的返回, 等待测试
            if content is None:
                return response.choices[0].message.tool_calls[0].function
            else:
                return content

    def _stream_run(self, messages: list) -> Generator[str, None, None]:
        """
        Run the assistant in a streaming manner with the given messages.

        Parameters
        ----------
        messages: list
            The messages which be used for call the LLM API.

        Returns
        -------
        generator
            The generator for the token(already be decoded) in assistant's messages.
        """

        return self.llm_client.stream_run(messages)

    def debug(self) -> dict[Any, Any]:
        """
        Reset the assistant's messages.

        Returns
        -------
        dict
            The last time the request messages and tools.
        """

        return self.last_request_info

    def _reset_default_list(self, parameter) -> tuple[list, Any]:
        """
        Reset the assistant's parameters to the default values.

        Parameters
        ----------
        parameter
            The parameter to reset.

        Returns
        -------
        tuple
            The value of this parameter in this time, and reset the parameter to None.
        """

        if parameter is None:
            local = []
        else:
            local = deepcopy(parameter)
            parameter = None

        return local, parameter

    def _complete_prompts(self, **kwargs) -> list:
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

            for i in range(len(current_messages)):
                current_messages[i]['content'] = current_messages[i]['content'].format(**kwargs)

            return current_messages
