""" 
============================
Memory Configuration Template
============================
"""

# Example
SINGLE_MEMORY_CONFIG = {
    "type": "milvus",
    "memory_name": "test_memory",
    "db_name": "test_db",
    "collection_name" : "test_memory",
    "partition_name" : "default",
    "if_partion_level" : False,
    "milvus_host" : '18.171.129.243',
    "milvus_port" : 80,
    "milvus_user" : "root",
    "milvus_psw" : "NetMindMilvusDB",
    "mongo_url" : "mongodb://NetMind:NetMindMongoDB@18.171.129.243:27017",
}

# Example
SET_MEMORY_CONFIG = {
    "metadata" : {
        "name": "test_memory",
        "create_data": "20xx-xx-xx",
    },

    "memorys_config":{
        "test_memory":
                        {
                        "type": "milvus",
                        "memory_name": "test_memory",
                        "db_name": "test_db",
                        "collection_name" : "test_memory",
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
                        "memory_name": "test_memory_2",
                        "db_name": "test_db_2",
                        "collection_name" : "test_memory_2",
                        "partition_name" : "default",
                        "if_partion_level" : False,
                        "milvus_host" : '18.171.129.243',
                        "milvus_port" : 80,
                        "milvus_user" : "root",
                        "milvus_psw" : "NetMindMilvusDB",
                        "mongo_url" : "mongodb://NetMind:NetMindMongoDB@18.171.129.243:27017",
                        },
    }
}

    

