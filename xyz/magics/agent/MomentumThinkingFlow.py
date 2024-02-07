import numpy as np
import re
from ThinkingFlow import ThinkingFlow
from CoreAgent import CoreAgent
from prompts import task_evaluating_prompt, task_dividing_prompt


# define energy identify and divide agent
task_evaluating_agent = CoreAgent(template=task_evaluating_prompt)
task_dividing_agent = CoreAgent(template=task_dividing_prompt)
agents_dict = {"task_evalutating_agent": task_evaluating_agent,
               "task_dividing_agent": task_dividing_agent}


#define momentum thinkingflow
class MomentumThinkingflow(ThinkingFlow):

    def __init__(self, agents_dict: dict = agents_dict, task_evaluating_agent:CoreAgent = task_evaluating_agent, task_dividing_agent:CoreAgent = task_dividing_agent):
        super().__init__(agents_dict)
        self.task_evaluating_agent = task_evaluating_agent
        self.task_dividing_agent = task_dividing_agent
        
    def get_energy(self, task:str, max_retry:int = 5) -> np.array:
        """Function for calculating energy for a task using agent

        Parameters
        ----------
        task : str
            The description of the task we are gonna evaluate
        
        Returns
        -------
        Currently a two dimensional array with the first indicating time energy and the second indicating complexity energy
        """
        retry_times = 0
        while retry_times<max_retry:
            try:
                estimated_energy_by_agent = self.task_evaluating_agent.run(current_task=task)
                energy_array = self.energy_extraction(estimated_energy_by_agent)
                break
            except:
                retry_times += 1
                print(f"retrying, this is {retry_times} time")
            
            
        return energy_array
    
    def energy_extraction(self, LLM_answer:str, pattern:str = r'Time needed:\n(\d+?) hours\n\nComplexity score:\n(\d+?)$') -> np.array:
        """The function to extract evaluated energy into multi-dimension np array from answer of LLM agents

        Parameters
        ----------
        LLM_answer : 
            LLM raw answer from task_evaluating_agent if energy not specified
        pattern : str, optional
            regular expression regex, by default r""

        Returns
        -------
        np.array
            multi-dimension array to express energy 
        """
        capture_match = re.search(pattern, LLM_answer)

        if capture_match:
            captured_parts = capture_match.groups()
            captured_parts = np.array([float(ele) for ele in captured_parts])
        else:
            raise Exception("no extracted energy using this pattern")
        
        return captured_parts
        