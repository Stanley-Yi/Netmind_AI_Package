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

from xyz.utils.llm.openai_key_holder import OpenAIKeyHolder
from xyz.node.agent import Agent

# from xyz.magics.thinkingflow.ThinkingFlow import ThinkingFlow


__all__ = ["LLMAgent"]


class LLMAgent(Agent):
    """ 
    An assistant that uses the LLM (Language Learning Model) for processing messages.
    """

    def __init__(self, template, core_agent, inner_multi=False, stream=False) -> None:
        """
        Initialize the LLMAgent.
        """
        super().__init__(core_agent)

        # TODO: 目前使用 单例模式，去请求 API，但是有个问题 是否在使用的时候 每一次的调用都希望能够 特殊化设置 生成参数
        self.core_agent = core_agent

        generate_parameters = {"inner_multi": inner_multi, "stream": stream}
        self.node_config = {"template": template,
                            "generate_parameters": generate_parameters}

        self.template = self.node_config['template']
        self.generate_parameters = self.node_config['generate_parameters']
        self.last_request_info = {}

    def flowing(self, messages=None, tools=[], **kwargs) -> str:
        """When you call this assistant, we will run the assistant with the given keyword arguments from the prompts.
            Before we call the OpenAI's API, we do some interface on this message.
        """

        if messages is None:
            local_messages = []
        else:
            local_messages = deepcopy(messages)
            messages = None    # This is necessary, because we need to reset the messages

        system_message, current_message = self._complete_prompts(**kwargs)
        # current_message = self._using_thinking_flow(system_message, user_message)

        local_messages.extend(current_message)
        return self.request(user_message=current_message, messages=local_messages, tools=tools)

    def request(self, user_message: List, messages: List, tools=[]) -> Any:
        """
        Run the assistant with the given keyword arguments.
        """

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

        # The reason why we not return the Generator is that we may need update the messages with inner_multi
        for word in self.core_agent.stream_run(messages):
            yield word

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

    def _using_thinking_flow(self, system_message: dict, user_message: dict) -> List:
        """
        Use the Thinking-Flow module to interface the system message and the user message.

        Parameters
        ----------
        system_message : dict
            The system message to interface.
        user_message : dict
            The user message to interface.

        Returns
        -------
        list
            A list containing the processed system message and user message.
        """
        # TODO: 我们的 Thinking-Flow 模块可以根据一些数据和条件 自主选择 是否要进行 prompts 的添加

        return [system_message, user_message]

