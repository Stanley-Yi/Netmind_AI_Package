"""
==================
TunePrompts
==================
@file_name: tune_prompts.py
@author: Tianlei Shi
@date: 2024-4-26
"""


__all__ = ["TunePrompts"]

import openai
from tqdm import tqdm
import itertools
from tenacity import retry, stop_after_attempt, wait_exponential
from copy import deepcopy

from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent
from xyz.utils.llm.openai_client import OpenAIClient


class TunePrompts(Agent):
    information: str
    llm_prompt_engineer: LLMAgent
    
    N_RETRIES = 3  # number of times to retry a call to the ranking model if it fails

    def __init__(self, core_agent: OpenAIClient) -> None:
        """
        The RankPrompts is a class to rank a list of prompts based on their performance.

        Parameters
        ----------
        generation_agent: OpenAIClient
            The agent to generate result according to specific prompt.
        score_agent: OpenAIClient
            The agent to score the performance of prompt's result.
        k: int
            A constant factor that determines how much ratings change.

        Examples
        --------
        >>> from xyz.utils.llm.openai_client import OpenAIClient
        >>> from xyz.function.rank_prompts import RankPrompts
        >>> generation_agent = OpenAIClient()
        >>> score_agent = OpenAIClient()
        >>> k = 32
        >>> gpt_prompt_engineer = GPTPromptEngineer(generation_agent, score_agent, k)
        >>> task = "Build a new prompt from solving k-12 math."
        >>> result = gpt_prompt_engineer(task=task)

        """
        super().__init__()

        # Set the information of the assistant. The information is used to help the user understand the assistant.
        self.set_information({
            "type": "function",
            "function": {
                "name": "GPTPromptEngineer",
                "description": "Generate an optimal prompt for a given task.",
                "parameters": {"test_cases": {"type": "list", "test_cases": "Some examples of the task."},
                               "description": {"type": "str", "description": "Description of the task which the user want to do."},
                               "prompts": {"type": "list", "prompts": "Prompts that need to be compared."}
                               },
                "required": ["test_cases", "description", "prompts"],
            },
        })
        self.output_type = "str"

        # Using the template we designed to define the assistant, which can do the main task.
        self.llm_generation_agent = LLMAgent(template=generation_prompt, llm_client=core_agent, stream=False)
        self.llm_improve_agent = LLMAgent(template=improve_prompt, llm_client=core_agent, stream=False)
    
    
    # Get Score - retry up to N_RETRIES times, waiting exponentially between retries.
    @retry(stop=stop_after_attempt(N_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=70))
    def get_new_prompt(self, messages, description, prompt, test_case, generation):
        
        return self.llm_improve_agent(messages=messages, description=description, prompt=prompt, test_case=test_case, generation=generation)
    
    
    @retry(stop=stop_after_attempt(N_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=70))
    def get_generation(self, prompt, test_case):

        return self.llm_generation_agent(prompt=prompt, test_case=test_case)
    

    def flowing(self, test_case, description, prompt, early_stop = 10) -> str:
        """
        The main function of the GPTPromptEngineer.

        Parameters
        ----------
        task: str
            The task which the user want to do.

        Returns
        -------
        str
            The prompts of the GPTPromptEngineer.
        """
        
        count = 0
        generation = None
        current_prompt = ''
        modified = prompt
        
        info = improve_prompt[1]['content'].format(description=description, prompt=prompt, test_case=test_case, generation=generation)
        messages = [{'role': 'user', 'content': info}]
                
        while count < early_stop and '|Finished|' not in modified:
            current_prompt = modified
            generation = self.get_generation(current_prompt, test_case)
            print(f"\n\nRound {count}: \n{generation}\n\n")
            
            modified = self.get_new_prompt(messages=messages, description=description, prompt=prompt, test_case=test_case, generation=generation)
            messages.append({'role': 'assistant', 'content': modified})
            
            count += 1
        
        if '|Finished|' in modified:
            return current_prompt
        
        return "Sorry, We did not achieve your requirement."

            



improve_prompt = [
    {"role": "system", "content": """Your job is to modify and improve prompts to meet user's requirements.
     
You will be provided with: 
* The task description - The requirements or results that user want to achieve;
* The current prompt - The prompt that need to modify and improve;
* The test case - A real use case, which will be used to test your final adjustments;
* The generation - Result that generated for the test case by using the current prompt.

You need to adjust the current prompt based on the information provided above, so that the results it generates can meet the needs of the user.


You need to first check whether the generation has met the user's needs:

If the user's requirements are not met, you need to modify the current prompt for the defective part.
As long as it meets the user's needs, you can significantly adjust the prompt, but you cannot change its original function; at the same time, you also need to refer to previous records to make better adjustments.
You need to directly return the modified prompt, omitting all explanations and instructions.

If the user's requirements are already met, you need to only return "|Finished|".
"""
    },
    {"role": "user", "content": """Task: {description}
     
Current Prompt: {prompt}

Test Case: {test_case}

Generation: {generation}
        """}
]


generation_prompt = [
    {"role": "system", "content": """{prompt}"""},
    {"role": "user", "content": "{test_case}"}
]