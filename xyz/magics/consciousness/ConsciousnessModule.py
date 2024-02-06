""" 
============
ConsciousnessModule
============
@file_name: ConsciousnessModule.py
@author: Hongyi.Gu, Tianlei.Shi, BlackSheep-Team, Netmind.AI
@date: 2024-2-6

"""


from xyz.magics.momentum.MomentumModule import MomentumModule


class ConsciousnessModule:
    
    def __init__(self):
        """Initiating Consciousness module with empty momentums
        """
        self.momentums = {} # Dictionary where key in id of ongoing momentum and value be their (energy, goal) pair
    
    def sort_momentum(self, inverse=True) -> list:
        """Sort priority of Momentums in self.momentums base on their energy and goals

        Parameters
        ----------
        inverse : bool, optional
            if the returned momentum list order from top priority to low priority or inversely, by default True

        Returns
        -------
        list
            list of momentum ids from top priority to low priority
        """
        raise NotImplementedError
    
    def choose_momentum(self, k=3) -> list:
        """Choose the top k priority momentum that not resolved

        Parameters
        ----------
        k : int, optional
            _description_, by default 3

        Returns
        -------
        list
            _description_
        """
        raise NotImplementedError
    
    def update_momentum_attributes(self, momentum_id, new_attributes) -> None:
        """Function for updating attribute in the momentum, incluing it attribute such as energy or feedback

        Parameters
        ----------
        momentum_id : str
            momentum_id for momentum in self.momentums to updata to
        new_attributes: dict
            new attributes value to update in momentum modules attribute dict
        """
        raise NotImplementedError
    
    def update_momentum_by_feedback(self, momentum_id, feedback) -> None:
        """Update the momentum from its feedback from the core LLM that process it. If it is finished: delete from momentem list and save in long term memory

        Parameters
        ----------
        momentum_id : str
            momentum_id for momentum in self.momentums to updata to
        feedback : str
            feedback from the core LLM processing the corresponding momentum
        """
        raise NotImplementedError