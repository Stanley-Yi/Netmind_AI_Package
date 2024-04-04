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
    An assistant that uses the LLM (Language Learning Model) for processing messages.

    Parameters
    ----------
    node_config : dict
        The configuration for the node.
    core_agent : CoreAgent
        The core assistant to use for requesting response from OpenAI.
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

    def flowing(self, messages=[], tools=[], **kwargs) -> str:
        """When you call this assistant, we will run the assistant with the given keyword arguments frsom the prompts.
            Before we call the OpenAI's API, we do some interface on this message.
            
        TODO: 为什么 messages 会被赋值？？？
        """
        system_message, current_message = self._complete_prompts(**kwargs)
        # current_message = self._using_thinking_flow(system_message, user_message)

        if self.generate_parameters["inner_multi"]:
            try:
                assert messages is None
            except:
                raise ValueError("The messages should be None when the inner-multi is True.")
            messages = self._get_messages(current_message)
            return self.request(user_message=current_message, messages=messages, tools=tools)  # TODO: 这个 User message 传的不优雅。

        else:
            return self.request(user_message=current_message, messages=current_message, tools=tools)

    def request(self, user_message: List, messages: List, tools=[]) -> Any:
        """
        Run the assistant with the given keyword arguments.
        """

        # TODO: 获取输出的时候，要进行参数的设置，参数的来源 self.generate_parameters
        if self.generate_parameters["stream"]:
            # If inner multi is True, we need to update the messages
            if self.generate_parameters["inner_multi"]:
                user_message.extend({"role": "assistant", "content": ""})
                self.add_messages(user_message)
            return self._stream_run(messages)
        else:
            print(f"This time mesages: {messages}")
            response = self.core_agent.run(messages, tools=tools)
            content = response.choices[0].message.content

            # TODO: 简单做了一个 tools 的调用的返回，还需要调试
            if content is None:
                return response.choices[0].message.tool_calls[0].function
            else:
                if self.generate_parameters["inner_multi"]:
                    user_message.extend({"role": "assistant", "content": ""})
                    self.add_messages(user_message)

            return content

    def _stream_run(self, messages: list) -> Generator[str, None, None]:
        """
        Run the assistant in a streaming manner with the given messages.
        """

        # The reason why we not return the Generator is that we may need update the messages with inner_multi
        for word in self.core_agent.stream_run(messages):
            if self.generate_parameters["inner_multi"]:
                self.messages[-1]["content"] += word
            yield word

    def reset_messages(self, messages=[]) -> None:
        """
        Reset the assistant's messages.

        Parameters
        ----------
        messages : list, optional
            The new messages for the assistant. Default is an empty list.
        """

        self.messages = messages

    def add_messages(self, messages: list) -> None:
        """
        Add messages to the assistant's messages.

        Parameters
        ----------
        messages : list
            The messages to add.
        """

        if self.generate_parameters["inner_multi"]:
            for message in messages:
                if message["role"] != "system":
                    self.messages.append(message)

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

        # TODO: 这个是旧版本的 prompts 的处理，之后会删除
        if type(self.template) == dict:
            system = self.template["system"]
            user = self.template["user"]

            self.prompts = system + "||--||" + user

            prefix = self.prompts.format(**kwargs)

            [system, user] = prefix.split("||--||")

            return {"role": "system", "content": system}, [{"role": "system", "content": system},
                                                           {"role": "user", "content": user}]

        elif type(self.template) == list:

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

    def _get_messages(self, current_message: List) -> List:
        """
        Set the assistant's messages based on the current message and the generate_parameters.

        Parameters
        ----------
        current_message : list
            The current message to use for setting the messages.

        Returns
        -------
        list
            The assistant's messages.
        """

        messages = deepcopy(self.messages)
        print("===出问题了")
        messages.extend(current_message)
        return messages

