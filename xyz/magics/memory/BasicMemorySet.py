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
from memory.BasicMemoryMechanism import BasicMemoryMechanism
from memory.BasicAttributeStorage import BasicAttributeStorage


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
            
    @staticmethod
    def load_milvus(memory_info):

        return BasicMemoryMechanism(
            memory_name=memory_info['memory_name'], 
            db_name=memory_info['db_name'], 
            collection_name = memory_info['collection_name'],
            partition_name = memory_info['partition_name'], 
            is_partion_level=memory_info['is_partion_level'], 
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
        
    def save_memorys(self):
        with open(self.info_path, 'w') as f:
            json.dump(self.info, f)
    
    def search_memory(self, memory_name, 
                        query: List[str], 
                        limit: int = 1000,  
                        replica_num: int = 1, 
                        doc_id_list: Optional[List[int]] = None,
                        meta_data_filter: Optional[Dict] = None,) -> List[Dict]:
        if self.info["memorys_config"][memory_name]["type"] != "milvus":
            raise TypeError("The this type of memory can not use search_memory")
        current_time = datetime.datetime.now()
        current_access_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        result = self._milvus_retrieval(memory_name,query, 
                    current_access_time,
                    limit,  
                    replica_num, 
                    doc_id_list,
                    meta_data_filter)
        return result           
    
    def _milvus_retrieval(self, memory_name, 
                        query: List[str], 
                        current_access_time: str,
                        limit: int = 1000,  
                        replica_num: int = 1, 
                        doc_id_list: Optional[List[int]] = None,
                        meta_data_filter: Optional[Dict] = None,) -> List[Dict]:
        return self.memory[memory_name].search_memory(
            query, 
            current_access_time,
            limit,  
            replica_num, 
            doc_id_list,
            meta_data_filter)
        
    def _no_sql_retrieval(self, memory_name,
                          attribute_group_name: str, 
                          attribute_type_name: str, 
                          key: str) -> Any:
        return self.memory[memory_name].get_attribute(
            attribute_group_name, 
            attribute_type_name, 
            key)
        
    def filter_memory(self, memory_name,
                        current_access_time: str,
                        limit: int = 1000,  
                        replica_num: int = 1, 
                        doc_id_list: Optional[List[int]] = None,
                        meta_data_filter: Optional[Dict] = None,) -> List[Dict]:
        return self.memory[memory_name].filter_memory(
                                                    current_access_time,
                                                    limit,  
                                                    replica_num, 
                                                    doc_id_list,
                                                    meta_data_filter)
        
    def add_memory(self, memory_name, 
                   meta_data_dict_list: List[Dict], 
                   description_list: List[str], 
                   full_content_dict_list: List[str]) -> None:
        current_time = datetime.datetime.now()
        current_access_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        save_time_list = [current_access_time] * len(meta_data_dict_list)
        
        self.memory[memory_name].add_memory(
            meta_data_dict_list, 
            description_list, 
            full_content_dict_list,
            save_time_list)
    
    def delate_memory(self, memory_info):
        raise NotImplementedError
    
    @staticmethod
    def read_json(json_path):
        with open(json_path, 'r') as f:
            return json.load(f)
        
