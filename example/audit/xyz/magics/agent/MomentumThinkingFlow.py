import numpy as np
import re
from xyz.magics.assistant.ThinkingFlow import ThinkingFlow
from xyz.magics.assistant.CoreAgent import CoreAgent
from xyz.magics.assistant.prompts import *


# define energy identify and divide assistant
task_evaluating_agent = CoreAgent(template=task_evaluating_prompt_new)
task_dividing_agent = CoreAgent(template=task_dividing_prompt_new)
agents_dict = {"task_evalutating_agent": task_evaluating_agent,
               "task_dividing_agent": task_dividing_agent}


#define momentum thinkingflow
class MomentumThinkingflow(ThinkingFlow):

    def __init__(self, agents_dict: dict = agents_dict, task_evaluating_agent:CoreAgent = task_evaluating_agent, task_dividing_agent:CoreAgent = task_dividing_agent):
        super().__init__(agents_dict)
        self.task_evaluating_agent = task_evaluating_agent
        self.task_dividing_agent = task_dividing_agent
        
    def get_energy(self, task:str, max_retry:int = 5) -> np.array:
        """Function for calculating energy for a task using assistant

        Parameters
        ----------
        task : str
            The description of the task we are gonna evaluate
        max_retry: int
            The max retry number when evaluating and extracting energy using agents to avoid circumstance the extraction failed because of format issue
        
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
                energy_array = 0
                print(f"retrying, this is {retry_times} time")
            
        if (energy_array==np.array(0)).all():
            print(f"the energy extraction failed, the answer by LLM is {estimated_energy_by_agent}")
        return energy_array
    
    def energy_extraction(self, LLM_answer:str, pattern:str = r'Time needed:\n(\d+?) hours\n\nComplexity score:\n(\d+?)$') -> np.array:
        """The function to extract evaluated energy into multi-dimension np array from answer of LLM agents

        Parameters
        ----------
        LLM_answer : 
            LLM raw answer from task_evaluating_agent if energy not specified
        pattern : str, optional
            regular expression regex, by default r'Time needed:\n(\d+?) hours\n\nComplexity score:\n(\d+?)$'

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
    
    def divide_task(self, task:str) -> list:
        """The function for dividing a given task into list of several subtask(step like)

        Parameters
        ----------
        task : str
            The current overwhelming task we want to divide

        Returns
        -------
        list
            List of small subtasks we want to achieve in a step like structure
        """
        try:
            task_breakdown_by_agent = self.task_dividing_agent.run(current_task=task)
            extract_divided_task = self.divided_tasks_extraction(divided_tasks=task_breakdown_by_agent)
        except:
            retry_times += 1
            print(f"retrying, this is {retry_times} time")
        
        if not extract_divided_task:
            extract_divided_task = []
        
        return  extract_divided_task
    
    def divided_tasks_extraction(self, divided_tasks:str, pattern:str = r"Step(\d+) \((initial|following Step(\d+)|option Step(\d+))\): ([^\n]+)((?:\n- [^\n]+)+)"):
        """The function for extracting divided tasks in to a subtask list using regular expression

        Parameters
        ----------
        divided_tasks : str
            The LLM raw answer from task_dividing_agent
        pattern : str
            regular expression regex, default r'## (Step \d+: [^\n]+)\n- ([\s\S]+?)(?=\n\n## Step \d+:|$)'
        """

        # Find all matches in the text
        matches = re.findall(pattern, divided_tasks)

        # Process matches to format them as required
        formatted_steps = []
        for match in matches:
            step_number = "Step" + match[0]
            step_reference = match[1]
            if step_reference.startswith('following'):
                step_reference = 'Step' + match[2]
            if  step_reference.startswith('option'):
                step_reference = 'Step' + match[3]
            step_content = match[4] + ' ' + ' '.join(match[5].strip().split('\n'))
            formatted_steps.append((step_number, step_reference, step_content))

        return formatted_steps