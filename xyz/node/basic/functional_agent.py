""" 
===============
FunctionalAgent
===============
@file_name: functional_agent.py
@author: Bin Liang
@date: 2023-2-29

"""


# python standard packages
import requests
import json
from typing import Any

# python third-party packages


# import from our tools
from xyz.node.basic.ABSAgent import ABSAgent
from xyz.utils.llm.openai_client import OpenAIClient
# from xyz.magics.thinkingflow.ThinkingFlow import ThinkingFlow


class FunctionalAgent(ABSAgent):
    """ 
    An assistant that uses a functional API for processing messages.

    Parameters
    ----------
    node_config : dict
        The configuration for the node.
    core_agent : OpenAIClient
        The core assistant to use for requesting response from OpenAI.
    """
    
    def __init__(self, node_config:dict, core_agent:OpenAIClient):
        """ 
        Initialize the FunctionalAgent.

        Parameters
        ----------
        node_config : dict
            The configuration for the node. It should contain the following keys:
            - 'api_url': The URL of the API.
            - 'headers': The headers for the API requests. If not provided, it will be set to None.
        core_agent : OpenAIClient
            The core assistant to use for requesting response from OpenAI.
        """
        
        self.url = node_config['api_url']
        
        if node_config['headers']:
            self.headers = node_config['headers']
        else:
            self.headers = None
            
        # TODO: 之后为了自主性，可以利用 core_agent 进行一些操作, 比如 在 call 之后，先利用大模型进行一些简单的处理，再去 request。
        self.core_agent = core_agent
        
    def __call__(self, parameters_dict:dict) -> Any:
        """When you start the current Agent, call this function directly, and this function will call the request function and return the result
            The reason for this is because there may be some other operations later

        Parameters
        ----------
        parameters_dict : dict
            The parameters to use for the api.

        Returns
        -------
        Any
            The response from the API.
        """
        return self.request(parameters_dict)
    
    def request(self, parameters_dict:dict) -> Any: 
        """ 
        Run the assistant with the given parameters.

        Parameters
        ----------
        parameters_dict : dict
            The parameters to use for running the assistant.

        Returns
        -------
        Any
            The response from the API.
        """
        
        # Step 1: 利用 OpenAI 的function call，直接获取到我们需要的信息。TODO: 如果使用的是其他的大模型，我们可能需要增加一些中间构建去获取，或者说我们要求 
        # 利用 function call 的时候 必须用 OpenAI 的API
        url = f"{self.url}process/"

        # response = requests.get(url)
        response = requests.post(url, json=parameters_dict, headers=self.headers)
        response_dict = json.loads(response.text)
        
        return response_dict["response"]
    
    def upload_file(self):
        raise NotImplemented 
    
    def download_file(self):
        raise NotImplemented
    
