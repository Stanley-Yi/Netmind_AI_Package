""" 
================
InputFormatAgent
================
@file_name: input_format_assistant.py
@author: Bin Liang
@date: 2024-3-14

"""


import json
from typing import Any

from xyz.node.basic.llm_agent import LLMAgent
from xyz.magics.assistant.operation_prompts import input_format_config

class InputFormatAgent(LLMAgent):
    
    def __init__(self, core_agent, node_config=input_format_config) -> None:
        super().__init__(node_config['template'], node_config['generate_parameters'], core_agent)
        
    def request(self, messages:list, tools:list=[]) -> tuple[Any, Any]:
        """
        Request the assistant to interface the messages.

        Parameters
        ----------
        messages : list
            A list of messages to be processed by the assistant.
        tools : list, optional
            A list of tools to be used by the assistant, by default [].

        Returns
        -------
        dict
            The assistant's response to the messages.
        """
        response = self.core_agent.run(messages, tools=tools) 
        function_infos = response.choices[0].message.tool_calls[0]
        
        parameters = function_infos['function']['arguments']
        parameters = parameters.replace("\n", "")
        parameters = json.loads(parameters)
        
        return function_infos, parameters



