"""
===========
MemoryAgent
===========
@file_name: MemoryAgent.py
@author: Bin Liang, BlackSheep-Team, Netmind.AI
@date: 2024-2-4

"""
    
    
import os
import json
from typing import Dict  
  
from xyz.magics.memory_client import MemoryClient


class MemoryAgent:
    
    def __init__(self, memory_client:MemoryClient, config_path:str) -> None: 
        """The assistant memory, which is used to connect to the memory server via the memory client.

        Parameters
        ----------
        memory_client : MemoryClient
            The memory client, which is used to connect to the memory server, and manage the memory units.
            The user should initialize the memory client before creating the assistant memory.
        config_path : str
            The path of the memory info file, which is used to store the memory configuration for this assistant.
        """
        
        self.memory_client = memory_client
        
        self.config_path = config_path
        if os.path.exists(self.config_path):
            self.config = self.memory_client.read_json(self.config_path)
        else:
            self.config = { "metadata": {},
                            "memorys_config": {}}
            
        self.memory_name = {}
        
        for memory_name, memory_config in self.config["memorys_config"].items():
            if memory_name not in self.memory_client.memory:
                self.connect_memory(memory_config, memory_name)
    
    def connect_memory(self, memory_config:Dict, memory_name:str, description:str="") -> None:
        """Connet to the memory server via the memory client, and create a memory unit in 
            the memory server if the memory is not in the client.

        Parameters
        ----------
        memory_config : Dict
            The memory config dict, which contains the memory type, memory name, and the memory configuration..
        memory_name : str
            The name of this memory
        description : str, optional
            The description of this memory, by default ""

        Raises
        ------
        TypeError
            We only support milvus and mongoDB two types of memory.
        """

        self.memory_client.connect_memory(memory_config=memory_config,
                                            memory_name=memory_name)

        self.memory_name[memory_name] = description
        
    def get_memory(self, memory_name:str = "default") -> None:
        """Get the memory unit from the memory client. 
        The you can use the memory unit to do the memory operations
        (To see the using methods, please see the BasicMemoryMechanism for the detail).

        Parameters
        ----------
        memory_name : str, optional
            The name of this memory, by default "default"

        Raises
        ------
        TypeError
            We only support milvus and mongoDB two types of memory.
        """
        
        if memory_name in self.memory_name:
            return self.memory_client.memory[memory_name]
        else:
            raise Exception("The memory name is not existed in this assistant.")
    
    def save_config(self) -> None:
        """To save this assistant memory configuration to the info file.
        """
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)   
        
    