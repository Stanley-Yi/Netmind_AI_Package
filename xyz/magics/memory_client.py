""" 
============
MemoryClient
============
@file_name: memory_client.py
@author: Bin.Liang, BlackSheep-Team, Netmind.AI
@date: 2024-2-1

"""


__all__ = ["MemoryClient"]

import os
import json
from typing import Dict

from xyz.magics.memory._memory_config_template import SINGLE_MEMORY_CONFIG    # preapre the checking of memory config template
from xyz.magics.memory.BasicMemoryMechanism import BasicMemoryMechanism
from xyz.magics.memory.BasicAttributeStorage import BasicAttributeStorage
from xyz.magics.memory.utils import singleclient


@singleclient   # We use the singleton pattern to create the memory client, which is used to connect to the memory server, and manage the memory units.
class MemoryClient:
    
    def __init__(self, config_path:str ) -> None:
        """To create a memory client, which is used to connect to the memory server, and manage the memory units. 
        All the memory should in one remote-server.
        In using, we should create a memory client be the global varivable. 
        For each assistant, we should connect to the real memory server via the memory client.

        Parameters
        ----------
        info_path : str
            The path of the memory info file, which is used to store the memory configuration.
        """
        
        self.config_path = config_path
        self.memory = {}
        
        if os.path.exists(self.config_path):
            self.config = self.read_json(self.config_path)
            self.memory_configs = self.config["memorys_config"]
        else:
            self.config = { "metadata": {},
                            "memorys_config": {}}
            self.save_config()

        for memory_name, memory_config in self.config["memorys_config"].items():
            self.connect_memory(memory_config, memory_name)

            
    def connect_memory(self, memory_config:Dict, 
                             memory_name:str = "default") -> None:
        """_summary_

        Parameters
        ----------
        memory_config : Dict
            The memory config dict, which contains the memory type, memory name, and the memory configuration..
            For detail, please read the README.md file in the memory folder.
        memory_name : str, optional
            The name of this memory, by default "default"

        Raises
        ------
        TypeError
            We only support milvus and mongoDB two types of memory.
        """
        
        # TODO: We should add the check of the memory_config. 
        
        memory_type = memory_config["type"]
        
        if memory_name == "default":
            memory_name = memory_config["memory_name"]
        else:
            memory_name = memory_name
        
        if memory_type == "milvus":
            self.memory[memory_name] = self.load_milvus(memory_config)
        elif memory_type == "nosql":
            self.memory[memory_name] = self.load_nosql(memory_config)
        else:
            raise TypeError("The type of memory is not supported.")
        
    def save_config(self):
        """To save this memory client configuration to the info file.
        """
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)      
                  
    @staticmethod
    def load_milvus(memory_info:Dict) -> BasicMemoryMechanism:
        """Load the milvus memory via the memory info.

        Parameters
        ----------
        memory_info : Dict
            The memory config of this milvus knowledge base

        Returns
        -------
        BasicMemoryMechanism
        """

        return BasicMemoryMechanism(
            memory_name=memory_info['memory_name'], 
            db_name=memory_info['db_name'], 
            collection_name = memory_info['collection_name'],
            partition_name = memory_info['partition_name'], 
            if_partion_level=memory_info['if_partion_level'], 
            milvus_host=memory_info['milvus_host'],
            milvus_port = memory_info['milvus_port'],
            milvus_user = memory_info['milvus_user'],
            milvus_psw = memory_info['milvus_psw'],
            mongo_url=memory_info['mongo_url'],
            )
    
    @staticmethod
    def load_nosql(memory_info:Dict) -> BasicAttributeStorage:
        """Load the nosql memory via the memory info.
        
        Parameters
        ----------
        memory_info : Dict
            The memory config of this mongoDB knowledge base
        
        """
        
        return BasicAttributeStorage(
            attribute_storage_name = memory_info['db_name'], 
            mongo_url= memory_info['mongo_url'])
    
    @staticmethod
    def read_json(json_path:str) -> Dict:
        """Load the json file to a dict.

        Parameters
        ----------
        json_path : str
            The path of the json file.

        Returns
        -------
        Dict
            The dict of the json file. In this project, whcih is a configuration of a memory-set.
        """
        
        with open(json_path, 'r') as f:
            return json.load(f)
        