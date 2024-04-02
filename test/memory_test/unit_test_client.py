import pytest
import json
from xyz.magics.memory_client import MemoryClient
from xyz.magics.memory.MemoryAgent import MemoryAgent


# Create the memory client.
@pytest.fixture(scope='module')
def client_create():
    
    client_config_path = "test/memory_test/test_client.json"
    # initialize the collection-level memory storage unit
    
    client_config = {
        "metadata" : {
            "name": "test_client",
            "create_data": "2024-02-04",
        },

        "memorys_config":{
            "test_memory_1":
                            {
                            "type": "milvus",
                            "memory_name": "client_test_collection_1",
                            "db_name": "client_test_db_1",
                            "collection_name" : "client_test_collection_1",
                            "partition_name" : "default",
                            "if_partion_level" : False,
                            "milvus_host" : '18.171.129.243',
                            "milvus_port" : 80,
                            "milvus_user" : "root",
                            "milvus_psw" : "NetMindMilvusDB",
                            "mongo_url" : "mongodb://NetMind:NetMindMongoDB@18.171.129.243:27017",
                            },
            "test_memory_2":
                            {
                            "type": "milvus",
                            "memory_name": "client_test_partition_1",
                            "db_name": "client_test_db_2",
                            "collection_name" : "niming",
                            "partition_name" : "client_test_partition_1",
                            "if_partion_level" : True,
                            "milvus_host" : '18.171.129.243',
                            "milvus_port" : 80,
                            "milvus_user" : "root",
                            "milvus_psw" : "NetMindMilvusDB",
                            "mongo_url" : "mongodb://NetMind:NetMindMongoDB@18.171.129.243:27017",
                            },
            }
        }
    
    with open(client_config_path, 'w') as f:
        json.dump(client_config, f)
    
    return MemoryClient(client_config_path)
    
# Create the memory assistant via client.
@pytest.fixture(scope='module')
def agent_create(client_create):
    
    agent_config_path = "test/memory_test/test_agent.json"
    # initialize the collection-level memory storage unit
    
    agent_config = {
        "metadata" : {
            "name": "test_agent",
            "create_data": "2024-02-04",
        },

        "memorys_config":{
            "test_memory_1":
                            {
                            "type": "milvus",
                            "memory_name": "client_test_collection_1",
                            "db_name": "client_test_db_1",
                            "collection_name" : "client_test_collection_1",
                            "partition_name" : "default",
                            "if_partion_level" : False,
                            "milvus_host" : '18.171.129.243',
                            "milvus_port" : 80,
                            "milvus_user" : "root",
                            "milvus_psw" : "NetMindMilvusDB",
                            "mongo_url" : "mongodb://NetMind:NetMindMongoDB@18.171.129.243:27017",
                            }
        }
    }
    
    with open(agent_config_path, 'w') as f:
        json.dump(agent_config, f)
    
    return MemoryAgent(client_create, agent_config_path)
    
def test_connect_memory(client_create):
    
    meta_data_dict_list = [{'importance': 10, 'area': 'london', 'mood': 'sad'},
                        {'importance': 8, 'area': 'nottinham', 'mood': 'extremely happy'},
                        {'importance': 2, 'area': 'birmingham', 'mood': 'peaceful'},
                        {'importance': 10, 'area': 'london', 'mood': 'fear'}]

    description_list = ['Eric found that he was rejected by his dream graph',
                    'Eric started his first dating activity with a girl',
                    'Eric took the bus to catch system engineering lecture in University of Birmingham as usual',
                    'Eric found that his roommate, Stanley is a gay who want to do something to him']

    full_contents_list = [{'content': 'Eric found that he was rejected by his dream graph'},
                      {'content': 'Eric started his first dating activity with a girl'},
                      {'content': 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'},
                      {'content': 'Eric found that his roommate, Stanley is a gay who want to do something to him'}]

    save_time = ['2024-01-09 12:12:53', '2024-02-10 12:12:53', '2024-01-25 12:12:53', '2024-04-01 12:12:53']

    result = client_create.memory["test_memory_1"].add_memory(meta_data_dict_list, description_list, full_contents_list, save_time)
    assert result == True
    
    
    
    