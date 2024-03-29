""" 
============
MomentumModule
============
@file_name: MomentumModule.py
@author: Hongyi.Gu, Tianlei.Shi, BlackSheep-Team, Netmind.AI
@date: 2024-2-6

"""


import numpy as np
from xyz.magics.memory.MemoryAgent import MemoryAgent
from xyz.magics.assistant.MomentumThinkingFlow import MomentumThinkingflow



class MomentumModule:
    
    def __init__(self, goal:str, longterm_memory:MemoryAgent, shortterm_memory, thinkingflow:MomentumThinkingflow, energy:float, decay_func, progress:float = 0, feedback:str = "None", actions = None, deadline:float=0, initial_type:str='child') -> None:
        """The momentum class of Agent, which has goal, energy to indicate attention needed and ability to be further divided into sub-momentums

        Parameters
        ----------
        goal : str
            The goal that assistant needs to finish in the momentum
        energy : np.array
            Energy is how the assistant is deciding on which task to do, when dividing task, energy will be divided as well
        longterm_memory : MemoryAgent
            The memory assistant, which connects to where past momentum and feedbacks are stored
        shortterm_memory : _type_
            Shortterm memory storing the current momentum and its parents, children
        progress : float
            Float from 0-1 to indicate the progress of current Momentum
        decay : function
            Function for energy decay, should accept variable with time and action
        feedback : str
            Feedback from core llm indicating the final result of the current momentum
        actions : None
            Available actions/tools to choose from and utilize
        initial_type : str
            The inital type of momentum when first created, should be "root" or "child"
        thinkingflow: N
        deadline: N
        """
        self.goal = goal
        self.energy = energy
        self.longterm_memory = longterm_memory
        self.shortterm_memory = shortterm_memory
        self.progress = progress
        self.feedback = feedback
        self.actions = actions
        self.thinkingflow = thinkingflow
        self.decay_func = decay_func
        self.initial_type = initial_type
        #self.get_momentum_energy()
        
        #if it is root momentum, automatically check for division
        if self.initial_type == 'root':
            self.decompose()
    
    def update_attributes(self) -> None:
        """funciton for manually update attributes in momentum class
        """
        raise NotImplementedError
    
    def get_momentum_energy(self, max_retry=5) -> None:
        """if user not specify energy of the momentum, determine the energy using agents
        
        Parameters
        ----------
        max_retry: int
            The max retry number when evaluating and extracting energy using agents to avoid circumstance the extraction failed because of format issue
        """
        # if not specified, return energy by assistant
        if (self.energy==np.zeros(2)).all():
            agent_extract_energy = self.thinkingflow.get_energy(task=self.goal, max_retry=max_retry)
            self.energy = agent_extract_energy
            
        return None

    def momentum_instuction(self) -> None:
        """Given the goal of momemtum and the actions(tools) store, give suggestion on how to carry on the momentum, update in goal
        """
        raise NotImplementedError
    
    def check_decompose(self) -> bool:
        """Check if the momentum needed to be decompose into submomentum if it is too complex base on its time to finish
        """
        decompose_threshold = np.array([50,50])
        comparision_result = np.all(self.energy < decompose_threshold)

        return not(comparision_result)
    
    def decompose(self) -> None:
        """Decompose the current momentum to smaller momentums with less energy and more specific goals, right now only happen it is a
        Root momentum and long term. The decompose will automatically be saved to short term memory
        """
        if self.check_decompose():
            subtasks = self.thinkingflow.divide_task(task=self.goal)
            
            # The subtask will be in form(Step, parent_step or initial if first, goal)
            #subtasks_with_energy = [MomentumModule(goal=task,longterm_memory=None, shortterm_memory=None, thinkingflow=self.thinkingflow) for task in subtasks]
        else:
            print('No need to decompose as the momentum is shortterm')
            subtasks= []

        return subtasks
    
    def decay(self, time, action_time) -> None:
        """Energy decay action associate with the time 

        Parameters
        ----------
        time : _type_
            _description_
        action_time : _type_
            _description_
        """
        raise NotImplementedError

    
    def save_to_short_memory(self) -> None:
        """function for storing and updating the short term memory, used when momentum divided, finished, or attributes changed
        """
        raise NotImplementedError
    
    def save_to_long_memory(self) -> None:
        """After the momentum is complete, save the momentum to the long term memory with past momentums and feedbacks, build link with its parent and sub momentums based on the short term memory
        """
        raise NotImplementedError