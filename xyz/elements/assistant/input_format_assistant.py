""" 
====================
InputFormatAssistant
====================
@file_name: input_format_assistant.py
@author: Bin Liang
@date: 2024-3-14
"""

__all__ = ["InputFormatAssistant"]

from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent
from xyz.utils.llm.openai_client import OpenAIClient


class InputFormatAssistant(Agent):
    information: str
    llm_input_format: LLMAgent

    def __init__(self, llm_client: OpenAIClient) -> None:
        """
        The InputFormatAssistant is a tool to help user using the function calling format to interface the messages.
        This assistant will call for the OpenAI API and use a tools list which is some callables object's information,
        to get the parameters dict for the next callable object which user want to use.

        Parameters
        ----------
        llm_client: OpenAIClient
            The core agent for the assistant, which can call the OpenAI API.

        Examples
        --------
        >>> from xyz.utils.llm.openai_client import OpenAIClient
        >>> from xyz.elements.assistant.input_format_assistant import InputFormatAssistant
        >>> core_agent = OpenAIClient()
        >>> assistant = InputFormatAssistant(llm_client)
        >>> ... # To define node_1 and node_2 are two callable objects.
        >>> node_1_parameter_1 = ""
        >>> node_1_parameter_2 = ""
        >>> node_1_parameter_3 = ""
        >>> output_1 = node_1(node_1_parameter_1=node_1_parameter_1,
        >>>                    node_1_parameter_2=node_1_parameter_2,
        >>>                    node_1_parameter_3=node_1_parameter_3)
        >>> node_2_parameters = assistant(input_content=output_1, tools=[node_2.information])
        >>> output = node_2_parameters(node_2_parameters)
        """
        super().__init__()

        # Set the information of the assistant. The information is used to help the user understand the assistant.
        self.set_information({
            "type": "function",
            "function": {
                "name": "InputFormatAssistant",
                "description": "Help user using the function calling format to interface the messages.",
                "parameters": {"last_node_input": {"type": "str", "description": "The input of the last node."},
                               "next_nodes_format": {"type": "list", "description": "The format of the next nodes."}
                               },
                "required": ["last_node_input", "next_nodes_format"],
            },
        })

        self.messages = []
        # Using the template we designed to define the assistant, which can do the main task.
        self.llm_input_format = LLMAgent(template=input_format_prompts, llm_client=llm_client, stream=False)

    def flowing(self, input_content: str, functions_list: list) -> dict:
        """
        The main function of the assistant, which can help user using the function calling format to interface
        the messages.

        Parameters
        ----------
        input_content: str
            The input of the last node.
        functions_list: list
            The list of OpenAI's Function call format information for some callables object.

        Returns
        -------
        dict
            The parameters dict for the next callable object which user want to use.
        """

        return self.llm_input_format(messages=self.messages, input_content=input_content, tools=functions_list)
    
    def add_history(self, messages: list) -> None:
        """
        Add messages to the assistant's global conversation history.

        Parameters
        ----------
        messages: list
            The list of messages to be added to the assistant's global conversation history.
        """
        self.messages.append(messages)


input_format_prompts = [
    {"role": "system", "content": """ 
Now, you are a work liaison and you need to assist with work communication.

Your task is to use tools to understand the natural language information at work, and translate it into a function 
calling format for output to the next worker. This helps the next person on the job understand the job better.

Requirements:
1. You will receive a natural language message as input.
2. You must use tools to understand this natural language information.
3. You must fully understand what the parameters of tools mean.
4. You must convert the natural language information into the function calling format and use the input information to 
define various parameters in the tool.
5. You have a global conversation history that you can use in this task. Sometimes the parameter information for the fucntion call you want to set is in the history dialog.

You are not allowed to fail, please be patient to complete this task.
Take a deep breath and start your work.
"""
     },

    {"role": "user", "content": """
The input in this time is : 
{input_content},
please choose a tool to interface this input.
Note: It is possible that the parameter information of the tool is in the history dialog. You can view the history dialog to get the parameter information of the tool. Please think carefully.
"""
    }
]
