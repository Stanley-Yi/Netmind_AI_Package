""" 
================
InputFormatAgent
================
@file_name: InputFormatAgent.py
@author: Bin Liang
@date: 2024-3-14

"""


import json
from typing import Tuple, Any

from xyz.node.basic.llm_agent import LLMAgent
from xyz.node.operation.operation_prompts import input_format_config

class InputFormatAgent(LLMAgent):
    
    def __init__(self, core_agent, node_config=input_format_config) -> None:
        super().__init__(node_config['template'], node_config['generate_parameters'], core_agent)
        
    def __call__(self, tools=[], **kwargs) -> str:
        super().__call__(tools=tools, **kwargs)
        
    def request(self, messages:list, tools:list=[]) -> tuple[Any, Any]:
        """
        Request the agent to interface the messages.

        Parameters
        ----------
        messages : list
            A list of messages to be processed by the agent.
        tools : list, optional
            A list of tools to be used by the agent, by default [].

        Returns
        -------
        dict
            The agent's response to the messages.
        """
        response = self.core_agent.run(messages, tools=tools) 
        function_infos = response.choices[0].message.tool_calls[0]
        
        parameters = function_infos['function']['arguments']
        parameters = parameters.replace("\n", "")
        parameters = json.loads(parameters)
        
        return function_infos, parameters



