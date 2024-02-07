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
from xyz.magics.agent.MomentumThinkingFlow import MomentumThinkingflow



class MomentumModule:
    
    def __init__(self, goal:str, longterm_memory:MemoryAgent, shortterm_memory, thinkingflow:MomentumThinkingflow, energy:np.array= np.zero(2), progress:float = 0, feedback:str = "None", actions = None) -> None:
        """The momentum class of Agent, which has goal, energy to indicate attention needed and ability to be further divided into sub-momentums

        Parameters
        ----------
        goal : str
            The goal that agent needs to finish in the momentum
        energy : np.array
            multidimensional vector indicating the energy level of the momentum, each dimension stands for diffent evaluation
        longterm_memory : MemoryAgent
            The memory agent, which connects to where past momentum and feedbacks are stored
        shortterm_memory : _type_
            shortterm memory storing the current momentum and its parents, children
        progress : float
            float from 0-1 to indicate the progress of current Momentum
        feedback : str
            feedback from core llm indicating the final result of the current momentum
        actions : None
            available actions/tools to choose from and utilize
        thinkingflow: N
        """
        self.goal = goal
        self.energy = energy
        self.longterm_memory = longterm_memory
        self.shortterm_memory = shortterm_memory
        self.progress = progress
        self.feedback = feedback
        self.actions = actions
        self.thinkingflow = thinkingflow
    
    def update_attributes(self) -> None:
        """funciton for manually update attributes in momentum class
        """
        raise NotImplementedError
    
    def momentum_energy(self, max_retry=5) -> None:
        """if user not specify energy of the momentum, determine the energy using agents
        
        Parameters
        ----------
        max_retry: int
            The max retry number when evaluating and extracting energy using agents to avoid circumstance the extraction failed because of format issue
        """
        # if not specified, return energy by agent
        if self.energy == np.zero(2):
            agent_extract_energy = self.thinkingflow.get_energy(task=self.goal, max_retry=max_retry)
            self.energy = agent_extract_energy
            
        return None

    def momentum_instuction(self) -> None:
        """Given the goal of momemtum and the actions(tools) store, give suggestion on how to carry on the momentum, update in goal
        """
        raise NotImplementedError
    
    def check_decompose(self) -> bool:
        """Check if the momentum needed to be decompose into submomentum if it is too complex base on energy and goals
        (currently using simple rules based on energy on time and complexity)
        """
        decompose_threshhold = np.array([50,50])
        comparision_result = np.all(self.energy < decompose_threshhold)

        return not(comparision_result)
    
    def decompose(self) -> list:
        """Decompose the current momentum to smaller momentums with less energy and more specific goals

        Returns
        -------
        list
            A list of subMomentums 
        """
        if self.check_decompose():
            subtasks = self.thinkingflow.divide_task(task=self.goal)
        
        return subtasks
    
    def save_to_short_memory(self) -> None:
        """function for storing and updating the short term memory, used when momentum divided, finished, or attributes changed
        """
        raise NotImplementedError
    
    def save_to_long_memory(self) -> None:
        """After the momentum is complete, save the momentum to the long term memory with past momentums and feedbacks, build link with its parent and sub momentums based on the short term memory
        """
        raise NotImplementedError