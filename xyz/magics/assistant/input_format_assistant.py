""" 
====================
InputFormatAssistant
====================
@file_name: input_format_assistant.py
@author: Bin Liang
@date: 2024-3-14

"""


from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent


class InputFormatAssistant(Agent):

    def __init__(self, core_agent) -> None:
        super().__init__()

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

        self.llm_input_format = LLMAgent(template=input_format_prompts, core_agent=core_agent, stream=False)

    def flowing(self, last_node_input: str, next_nodes_format: list) -> dict:
        """
        Request the assistant to interface the messages.
        """

        return self.llm_input_format(last_node_input=last_node_input, tools=next_nodes_format)


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

You are not allowed to fail, please be patient to complete this task.
"""},
    {"role": "user", "content": """
The input in this time is : 
{input},
please choose a tool to interface this input.
"""
     }]
