""" 
========
LLMAgent
========
@file_name: llm_agent.py
@author: Bin Liang
@date: 2023-2-29

"""


from copy import deepcopy
from typing import Generator, List, Any, Dict

from xyz.utils.llm.openai_key_holder import OpenAIKeyHolder
from xyz.node.agent import Agent
# from xyz.magics.thinkingflow.ThinkingFlow import ThinkingFlow


__all__ = ["LLMAgent"]


class LLMAgent(Agent):
    """ 
    An agent that uses the LLM (Language Learning Model) for processing messages.

    Parameters
    ----------
    node_config : dict
        The configuration for the node.
    core_agent : CoreAgent
        The core agent to use for requesting response from OpenAI.
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
        self.messages = []

        self._set_prompts()

    def flowing(self, messages=[], tools=[], **kwargs) -> str:
        """When you call this agent, we will run the agent with the given keyword arguments from the prompts.
            Before we call the OpenAI's API, we do some interface on this message.

        Returns
        -------
        str
            The response from the OpenAI's API
        """
        [system_message, user_message] = self._complete_prompts(**kwargs)
        current_message = self._using_thinking_flow(system_message, user_message)

        if self.generate_parameters["inner_multi"]:
            try:
                assert messages is None
            except:
                raise ValueError("The messages should be None when the inner-multi is True.")
            messages = self._get_messages(current_message)
            return self.request(user_message=user_message, messages=messages, tools=tools)  # TODO: 这个 User message 传的不优雅。

        else:
            messages.extend(current_message)
            return self.request(user_message=user_message, messages=messages, tools=tools)

    def request(self, user_message: Dict, messages: List, tools=[]) -> Any:
        """
        Run the agent with the given keyword arguments.

        Parameters
        ----------
        tools
        messages
        user_message
        **kwargs
            The keyword arguments to use for running the agent.

        Returns
        -------
        str
            The agent's response.
        """

        # TODO: 获取输出的时候，要进行参数的设置，参数的来源 self.generate_parameters
        if self.generate_parameters["stream"]:
            # If inner multi is True, we need to update the messages
            if self.generate_parameters["inner_multi"]:
                self.add_messages([user_message, {"role": "assistant", "content": ""}])
            return self._stream_run(messages)
        else:
            response = self.core_agent.run(messages, tools=tools)
            content = response.choices[0].message.content

            # TODO: 简单做了一个 tools 的调用的返回，还需要调试
            if content is None:
                return response.choices[0].message.tool_calls[0].function
            else:
                if self.generate_parameters["inner_multi"]:
                    self.add_messages([user_message, {"role": "assistant", "content": content}])

            return content

    def _stream_run(self, messages: list) -> Generator[str, None, None]:
        """
        Run the agent in a streaming manner with the given messages.

        Parameters
        ----------
        messages : list
            The messages to use for running the agent.

        Yields
        ------
        str
            The agent's response, yielded one piece at a time.
        """

        # The reason why we not return the Generator is that we may need update the messages with inner_multi
        for word in self.core_agent.stream_run(messages):
            if self.generate_parameters["inner_multi"]:
                self.messages[-1]["content"] += word
            yield word

    def reset_messages(self, messages=[]) -> None:
        """
        Reset the agent's messages.

        Parameters
        ----------
        messages : list, optional
            The new messages for the agent. Default is an empty list.
        """

        self.messages = messages

    def add_messages(self, messages: list) -> None:
        """
        Add messages to the agent's messages.

        Parameters
        ----------
        messages : list
            The messages to add.
        """

        if self.generate_parameters["inner_multi"]:
            for message in messages:
                if message["role"] != "system":
                    self.messages.append(message)

    def _set_prompts(self) -> None:
        """
        Set the agent's prompts based on its template.
        """

        system_message = self.template["system"]
        user_message = self.template["user"]

        self.prompts = system_message + "||--||" + user_message

    def _complete_prompts(self, **kwargs) -> tuple:  # TODO: 这里的返回值不够明确
        """
        Complete the agent's prompts with the given keyword arguments.

        Parameters
        ----------
        **kwargs
            The keyword arguments to use for completing the prompts.

        Returns
        -------
        tuple
            A tuple containing the system message and the user message.
        """

        system = self.template["system"]
        user = self.template["user"]

        self.prompts = system + "||--||" + user

        prefix = self.prompts.format(**kwargs)

        [system, user] = prefix.split("||--||")

        return {"role": "system", "content": system}, {"role": "user", "content": user}

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

    def _get_messages(self, current_message: List) -> List:
        """
        Set the agent's messages based on the current message and the generate_parameters.

        Parameters
        ----------
        current_message : list
            The current message to use for setting the messages.

        Returns
        -------
        list
            The agent's messages.
        """

        messages = deepcopy(self.messages)
        messages.extend(current_message)
        return messages

