""" 
==============
BasicMemorySet
==============
@file_name: BasicMemorySet.py
@author: Bin.Liang, BlackSheep-Team, Netmind.AI
@date: 2024-2-1
Combain many BMM in one set, and provide the basic operation for the set. We also add more high level operation for the set.
"""


import os
import json
from datetime import datetime
from user_settings import DEFAULT_INFO
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus
from xyz.magics.memory._memory_config_template import MEMORY_CONFIG
from xyz.magics.memory.BasicMemoryMechanism import BasicMemoryMechanism
from xyz.magics.memory.BasicAttributeStorage import BasicAttributeStorage


class BasicMemorySet:
    
    def __init__(self, info_path, db_name="default_db") -> None:
        
        self.info_path = info_path
        
        if os.path.exists(self.info_path):
            self.info = self.read_json(self.info_path)
        else:
            self.info = {"if_init" : False}
        
        if self.info["if_init"]:
            memorys_config = self.info['memorys_config'] 
            self.memory = {}
            for memory_name, memory_config in memorys_config.items():
                self.connect_memory(memory_config, memory_name)
        else:
            self.info = DEFAULT_INFO
            if db_name == "default_db":
                raise ValueError("The default db name is not set.")
            self.info["default_db_name"] = db_name
            self.info['memorys_config'] = {}
            
    def connect_memory(self, memory_config=MEMORY_CONFIG, memory_name="default"):
        
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
        with open(self.info_path, 'w') as f:
            json.dump(self.info, f)      
                  
    @staticmethod
    def load_milvus(memory_info):

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
    def load_nosql(memory_info):
        return BasicAttributeStorage(
            attribute_storage_name = memory_info['db_name'], 
            mongo_url= memory_info['mongo_url'])
    
    @staticmethod
    def read_json(json_path):
        with open(json_path, 'r') as f:
            return json.load(f)
        
