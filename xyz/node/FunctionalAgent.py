""" 
===============
FunctionalAgent
===============
@file_name: FunctionalAgent.py
@author: Bin Liang
@date: 2023-2-29

"""


# python standard packages
import requests
import json

# python third-party packages


# python first-party packages
from xyz.node.ABSAgent import ABSAgent
from xyz.node.CoreAgent import CoreAgent
# from xyz.magics.thinkingflow.ThinkingFlow import ThinkingFlow


class FunctionalAgent(ABSAgent):
    """ 
    An agent that uses a functional API for processing messages.

    Parameters
    ----------
    node_config : dict
        The configuration for the node.
    core_agent : CoreAgent
        The core agent to use for requesting response from OpenAI.
    """
    
    def __init__(self, node_config, core_agent):
        """ 
        Initialize the FunctionalAgent.

        Parameters
        ----------
        node_config : dict
            The configuration for the node. It should contain the following keys:
            - 'api_url': The URL of the API.
            - 'api_name': The name of the API.
            - 'description': The description of the API.
            - 'parameters': The parameters for the API.
            - 'headers': The headers for the API requests. If not provided, it will be set to None.
        core_agent : ABSAgent
            The core agent to use for processing messages.
        """
        
        self.url = node_config['api_url']
        
        self.api_name = node_config['api_name']        
        self.description = node_config['description']
        self.parameters = node_config['parameters']  
        
        if node_config['headers']:
            self.headers = node_config['headers']
        else:
            self.headers = None
            
        # TODO: 之后为了自主性，可以利用 core_agent 进行一些操作
        self.core_agent = core_agent
    
    def run(self, parameters_dict:dict) -> str: 
        """ 
        Run the agent with the given parameters.

        Parameters
        ----------
        parameters_dict : dict
            The parameters to use for running the agent.

        Returns
        -------
        str
            The response from the API.
        """
        
        # Step 1: 利用 OpenAI 的function call，直接获取到我们需要的信息。TODO: 如果使用的是其他的大模型，我们可能需要增加一些中间构建去获取，或者说我们要求 
        # 利用 function call 的时候 必须用 OpenAI 的API
        url = f"{self.url}process/"

        # response = requests.get(url)
        response = requests.post(url, json=parameters_dict, headers=self.headers)
        response_dict = json.loads(response.text)
        
        return response_dict["response"]
    
    def get_api_info(self) -> str:
        """
        Get the API's description.

        Returns
        -------
        str
            The description of the API.
        """
        
        return self.description
    
    def get_function_call_info(self):
        """
        Get the information for calling the function.

        Returns
        -------
        dict
            A dictionary containing the information for calling the function. It includes the following keys:
            - 'type': The type of the call, which is "function".
            - 'function': A dictionary containing the function's name, description, and parameters.
        """

        return {
            "type": "function",
            "function": {
                "name": self.api_name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        self.parameters
                    },
                    "required": self.parameters.keys(),
                },
            },
        }

