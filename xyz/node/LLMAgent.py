""" 
========
LLMAgent
========
@file_name: LLMAgent.py
@author: Bin Liang
@date: 2023-2-29

"""


from copy import deepcopy
from typing import Any, Generator

from xyz.node.ABSAgent import ABSAgent
# from xyz.magics.thinkingflow.ThinkingFlow import ThinkingFlow


class LLMAgent(ABSAgent):
    """ 
    An agent that uses the LLM (Language Learning Model) for processing messages.

    Parameters
    ----------
    node_config : dict
        The configuration for the node.
    core_agent : CoreAgent
        The core agent to use for requesting response from OpenAI.
    """
    
    def __init__(self, node_config, core_agent) -> None:
        """
        Initialize the LLMAgent.

        Parameters
        ----------
        node_config : dict
            The configuration for the node.
        core_agent : CoreAgent
            The core agent to use for requesting response from OpenAI.
        """
        ABSAgent.__isabstractmethod__ = True
        
        # TODO: 目前使用 单例模式，去请求 API，但是有个问题 是否在使用的时候 每一次的调用都希望能够 特殊化设置 生成参数
        self.core_agent = core_agent
        self.template = node_config['template']
        self._set_prompts()
        self.generate_parameters = node_config['generate_parameters']
        self.messages = []
        
    def __call__(self, **kwargs) -> str:
        """When you call this agent, we will run the agent with the given keyword arguments from the prompts.
            Before we call the OpenAI's API, we do some process on this message.

        Returns
        -------
        str
            The response from the OpenAI's API
        """
        
        # TODO: 异常处理
        
        [system_message, user_message] = self._complete_prompts(**kwargs)
        current_message = self._using_thinking_flow(system_message, user_message)
        messages = self._get_messages(current_message)
        
        return self.request(user_message=user_message, messages=messages)   # TODO: 这个 User message 传的不优雅。
    
    def request(self, user_message:dict, messages:list) -> str:
        """
        Run the agent with the given keyword arguments.

        Parameters
        ----------
        **kwargs
            The keyword arguments to use for running the agent.

        Returns
        -------
        str
            The agent's response.
        """
        
        # TODO: 获取输出的时候，要进行参数的设置，参数的来源 self.generate_parameters
        if self.generate_parameters["if_stream"]:  
            self.add_messages([user_message, {"role": "assistant", "content": ""}])
            return self._stream_run(messages)
        else:
            response = self.core_agent.run(messages) 
            self.add_messages([user_message, {"role": "assistant", "content": response}])
            return response
    
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
        
        response = ""
        for word in self.core_agent.stream_run(messages):
            response += word
            self.messages[-1]["content"] = response
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
        
    def add_messages(self, messages) -> None:
        """
        Add messages to the agent's messages.

        Parameters
        ----------
        messages : list
            The messages to add.
        """
        
        if self.generate_parameters["if_multi"]:
            for message in messages:
                if message["role"] != "system":
                    self.messages.append(message)
    
    def _set_prompts(self) -> None:
        """
        Set the agent's prompts based on its template.
        """
        
        system = self.template["system"]
        user = self.template["user"]

        self.prompts = system + "||--||" + user    
        
    def _complete_prompts(self, **kwargs) -> tuple: # TODO: 这里的返回值不够明确
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
       
    def _using_thinking_flow(self, system_message:dict, user_message:dict) -> list:
        """
        Use the Thinking-Flow module to process the system message and the user message.

        Parameters
        ----------
        system_message : dict
            The system message to process.
        user_message : dict
            The user message to process.

        Returns
        -------
        list
            A list containing the processed system message and user message.
        """
        # TODO: 我们的 Thinking-Flow 模块可以根据一些数据和条件 自主选择 是否要进行 prompts 的添加
        
        return [system_message, user_message]
        
    def _get_messages(self, current_message: list) -> list:
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
        
        if self.generate_parameters["if_multi"]:
            messages = deepcopy(self.messages)
            messages.extend(current_message)
            return messages
        else:
            return current_message
    
