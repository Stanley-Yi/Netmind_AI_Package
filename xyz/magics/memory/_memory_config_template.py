""" 
============================
Memory Configuration Template
============================
"""


# The default memory configuration is used to initialize the memory mechanism.
# And we also set the default memory configuration 
MEMORY_CONFIG = {
    "type": "milvus",
    "if_init" : True,
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



