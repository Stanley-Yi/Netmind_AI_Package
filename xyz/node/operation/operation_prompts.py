""" 
==============
system_prompts
==============
@file_name: operation_prompts.py
@author: Bin Liang
@date: 2024-3-14 
This file contains the system prompts for the node.
"""


system_generation_parameters = { "llm": "gpt-4-1106-preview", "temperature" : 0, 'if_multi':False, 'if_stream' : False}

input_format_prompts = {"system" : """ 
Now, you are a work liaison and you need to assist with work communication.

Your task is to use tools to understand the natural language information at work, and translate it into a function calling format for output to the next worker. This helps the next person on the job understand the job better.

Requirements:
1. You will receive a natural language message as input.
2. You must use tools to understand this natural language information.
3. You must fully understand what the parameters of tools mean.
4. You must convert the natural language information into the function calling format and use the input information to define various parameters in the tool.

You are not allowed to fail, please be patient to complete this task.
""", "user" : """
The input in this time is : 
{input},
please choose a tool to interface this input.
""" 
}

input_format_config = {

    "template": input_format_prompts,
    "generate_parameters": system_generation_parameters

}



