"""
====================
BasicMemoryMechanism
====================
@file_name: BasicMemoryMechanism.py
@author: Zhouhan Zhang, BlackSheep-Team, Netmind.AI
@date: 2024-1-31
The basic memory object, which has function for modifying memory include saving, loading, retrieving
"""


import time
from pymilvus import connections
from pymongo import MongoClient
from typing import Dict, List, Optional, Any
from pymilvus import db, Collection
from pymilvus import utility
from pymilvus import CollectionSchema, FieldSchema, DataType

from netmindxyz.magics.memory.utils import attach_idx, generate_int64_id, is_valid_timestamp, append_expr
from netmindxyz.magics.memory._embedding_setting.EmbeddingTypeEnum import EmbeddingType
from netmindxyz.magics.memory._embedding_setting.IdxTypeEnum import IdxType
from netmindxyz.magics.memory._embedding_setting.MetricTypeEnum import MetricType

import os
from openai import OpenAI
os.environ["OPENAI_API_KEY"] = "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"

client = OpenAI(
    api_key = os.environ.get(
        "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"),
)

import sys
sys.path.append("..")

API_KEY = "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"

class BasicMemoryMechanism:

    def __init__(
            self,
            memory_name: str, 
            db_name: str,
            coll_name: str = None,
            is_partion_level: bool = False,
            milvus_host: str = 'localhost', 
            milvus_port: int = 19530, 
            milvus_user: str = 'root',
            milvus_psw: str = 'NetMindMilvusDB',
            mongo_url: str = 'mongodb://localhost:27017/', 
            # The following parameters always be uesed in default
            storage_engine: str = 'default',
            num_shards: int = 1,
            embedding_type: EmbeddingType = EmbeddingType.OpenAI_text_embedding_ada_002, 
            metric_type: MetricType = MetricType.L2, 
            idx_type: IdxType = IdxType.IVF_FLAT, 
            **idx_builder):
        """The basic memory object, which has function for modifying memory include saving, loading, retrieving

        Parameters
        ----------
        memory_name : str
            the name of this memory storage
        db_name : str
            the name of used Milvus database
        coll_name : str
            the name of used Milvus collection
        is_partion_level : bool
            indicating the type of memory unit storage: true if it is partition-level; false if it is collection-level
        milvus_host : str
            the host of deployed milvus vector database
        milvus_port : str
            the port of deployed milvus vector database
        milvus_user : str
            the user name to log into Milvus vector database
        milvus_psw : str
            the password to log into Milvus vector database
        storage_engine : str
            specify in which server the collection is to be created; in Milvus cluster, there can be more than one server, each server will have a server alias
        num_shards : int
            specify the amount of nodes that one write operation in collection is distributed to, thus enhence the capabality of parallel computing potential of Milvus cluster
        mongo_url : str
            the url of deployed mongoDB server
        embedding_type : EmbeddingType
            the embedding algorithm to be use when embedding the description sentence into a vector
        metric_type : MetricType
            the algorithm used to measure similarity among different vectors
        idx_type : IdxType
            the in-memory indexes supported by milvus, which can be configured to achieve better search performance
        """
        self.milvus_connection = { "host": milvus_host, "port": milvus_port, "user": milvus_user, "password": milvus_psw,
                                  "is_partion_level":is_partion_level}
        # Step 1: connect to the Milvus vector database
        try:
            connections.connect(host=milvus_host, port=milvus_port, user=milvus_user, password=milvus_psw)
        except:
            raise Exception('Milvus connect failed: the host or port you provided is not correct')
        
        '''
        The memory records are stored in a single database within Milvus database; 
        each database contains multiple collections; each collections contains multiple partitions; the memory records are actually stored in each partitions
        This BasicMemoryMechanism facilitates two types of memory unit storage levels available, ie, collection-level and partition-level

        - if it is collection-level: The collection is named as memory_name, and all of its memory records are stored in 'default' partition
        - if it is partiton-level: The collection is named as a pre-specified name, and a partition named as memory_name will be created and used within this collection
        '''

        # Step 2: connect to the MongoDB no-SQL database
        self._mongo_db = None
        try:
            client = MongoClient(mongo_url)
            self._mongo_db = client[memory_name] # connect to mongoDB client, and use the database, whose name is memory_name
            self.mongo_url = mongo_url
        except Exception as e:
            raise Exception('Milvus connect failed: the host or port you provided is not correct')
        
        '''
        The info format of registered_attributes related to a single memory unit is:

        In database - memory_name:
        In collection - 'registered_attributes':
        [
            {
                ''attributes'': list(),
            }
        ]
        '''
        
        '''
        The format of attribute dict related to a single memory unit is:

        In database - memory_name:
        In collection - memory_group [for example, we set a group named milvus_data to store save_time and last_access_time properties for each memory records]:
        [
            {
            
                'attribute_type': attribute_type_1,
                'values': { property_1: value_1, property_2: value_2, property_3: value_3 }
            }

            {
                'attribute_type': attribute_type_1,
                'values': { property_1: value_1, property_2: value_2, property_3: value_3 }
            }
        ]
        '''
    
        self.memory_name = memory_name
        self.collection_name = coll_name
    
        # parameters related to milvus settings
        self._storage_engine = storage_engine
        self.collection = None
        self.db_name = db_name
        self.partition_name = memory_name if is_partion_level else 'default'
        self._search_idx_params = None
        
        # parameters related to embedding
        self._embedding_type = embedding_type
        self.metric_type = metric_type

        # initialize the collection instance
        if not self._load_memory_store(
                    coll_name if is_partion_level else memory_name, 
                    num_shards, 
                    metric_type, 
                    idx_type, 
                    idx_builder=idx_builder):
            raise Exception('loading memory store failed')

    def get_info(self):
        return { "db_name" : self.db_name, 
                "collection_name" : self.collection_name,
                "memory_name" : self.partition_name,
                "is_partion_level" : self.milvus_connection['is_partion_level'],
                "milvus_host" : self.milvus_connection['host'], 
                "milvus_port" : self.milvus_connection['port'], 
                "milvus_user" : self.milvus_connection['user'], 
                "milvus_psw" : self.milvus_connection['password'], 
                "mongo_url" : self.mongo_url,
                "meta_data" : {
                    "embedding_type" : self._embedding_type,
                    "metric_type" : self.metric_type,
                }}
    
    def update_attributes(
            self, 
            collection_name: str, 
            attribute_type: str, 
            key: str, 
            value: Any) -> bool:
        """Insert or update the attribute value into mongoDB

        Parameters
        ----------
        collection_name : str
            the name of collection, in which certain group of documents is stored
        attribute_type : str
            the type of attribute, which is corresponding to a set of different key-value properties
        key : str
            the name of key, which is used to select value from key-value properties that is corresponding to given attribute_type
        value : Any
            the new value to be stored, the type depends on given value
            
        Returns
        -------
        bool
            indicating whether the new value is inserted into mongoDB successfully
       """
        # firstly, check out if the given attribute_type already registered into the mongoDB database
        if 'registered_attributes' not in self._mongo_db.list_collection_names():
            self._mongo_db['registered_attributes'].insert_one({'attributes' : list()})

        old_registered_value = self._mongo_db['registered_attributes'].find()[0]
        registered_attributes = old_registered_value['attributes'].copy()

        registered = str(attribute_type) + 'in' + collection_name

        if registered not in registered_attributes:
            # if the attribute_type is not registered, do the insertion; and register the new attribute_type to the mongoDB
            data = {}
            data['attribute_type'] = attribute_type
            data['values'] = {key: value}
            operation_1 = self._mongo_db[collection_name].insert_one(data)

            registered_attributes.append(registered)
            operation_2 = self._mongo_db['registered_attributes'].update_one(filter=old_registered_value, update={'$set': {'attributes': registered_attributes}})

            return operation_1.inserted_id is not None and operation_2.modified_count == 1
        else:
            # if the attribut_type is registered, get the full origin json data mapped to key 'values', and do the update
            values_json = self._mongo_db[collection_name].find_one({'attribute_type': attribute_type})['values'].copy()
            values_json[key] = value

            operation = self._mongo_db[collection_name].update_one(filter={'attribute_type': attribute_type}, update={'$set': {'values': values_json}})

            return operation.modified_count == 1

    def get_attribute(
            self, 
            collection_name: str, 
            attribute_type: str, 
            key: str,) -> Any:
        """Get the attribute value from mongoDB

        Parameters
        ----------
        collection_name : str
            the name of collection, in which certain group of documents is stored
        attribute_type : str
            the type of attribute, which is corresponding to a set of different key-value properties
        key : str
            the name of key, which is used to select value from key-value properties that is corresponding to given attribute_type

        Returns
        -------
        Any
            depends on the type of fetched value
       """
        # firstly, check out if the given attribute_type already registered into the mongoDB database
        if 'registered_attributes' not in self._mongo_db.list_collection_names():
            raise Exception('Currently there is no attributes registered yet')
        
        registered_attributes = self._mongo_db['registered_attributes'].find()[0]['attributes']
        registered = attribute_type + 'in' + collection_name

        if registered not in registered_attributes:
            raise Exception('the specified attribute_type does not exist')

        values_json = self._mongo_db[collection_name].find_one({'attribute_type': attribute_type})['values']

        try:
            return values_json[key]
        except KeyError:
            raise Exception('the specified key does not exist, or does not belong to given attribute type')

    def delete_attribute(
            self, 
            collection_name: str, 
            attribute_type: str, ) -> bool:
        """Delete the document related to given attribute_type from mongoDB

        Parameters
        ----------
        collection_name : str
            the name of collection, in which certain group of documents is stored
        attribute_type : str
            the type of attribute, which is corresponding to a set of different key-value properties

        Returns
        -------
        bool
            indicating whether deleting documents from mongoDB is successful
        """

        if 'registered_attributes' not in self._mongo_db.list_collection_names():
            raise Exception('Currently there is no attributes registered yet')

        old_registered_value = self._mongo_db['registered_attributes'].find()[0]
        registered_attributes = old_registered_value['attributes'].copy()
        registered = attribute_type + 'in' + collection_name

        if registered not in registered_attributes:
            raise Exception('the specified attribute_type does not exist')

        operation_1 = self._mongo_db[collection_name].delete_one({'attribute_type': attribute_type})
        
        registered_attributes = registered_attributes
        registered_attributes.remove(registered)
        operation_2 = self._mongo_db['registered_attributes'].update_one(filter=old_registered_value, update={'$set': {'attributes': registered_attributes}})

        return operation_1.deleted_count == 1 and operation_2.modified_count == 1

    def _get_embedding(
            self, 
            content: List[str],) -> List[List[float]]:
        """Given a list of content strings, use the chosen embeddeing type to do the embeddings
        
        Parameters
        ----------
        content : List[str]
            the list of content strings

        Returns
        -------
        List[List[float]]
            the list of embedding vectors
        """ 
        
        # check the length of content
        if not content:
            return []
        
        content_len = len(content)
        
        embedding_res = []
        
        try:
            start = time.perf_counter()
            scale = 50
            
            for i in range(content_len):
                fill_length = int(scale * (i + 1) / content_len)
                a = "*" * fill_length
                b = "." * (scale - fill_length)
                
                respond = client.embeddings.create(
                    model=self._embedding_type.model,
                    input=content[i],
                    encoding_format= "float"
                )
                embedding_res.append(respond.data[0].embedding)
                
                dur = time.perf_counter() - start
                print("\r{}/{}[{}->{}]{:.2f}s".format(i + 1, content_len, a, b, dur),end = "")
                
        except Exception as err:
            raise err
        
        return embedding_res

    def _load_memory_store(
            self, 
            collection_name: str,
            num_shards: int,
            metric_type: MetricType,
            idx_type: IdxType,
            **idx_builder,) -> bool:
        """Load the collection instance, if there is no such collection exsist, create a new one
        
        Parameters
        ----------
        collection_name : str
            the name of used Milvus collection
        num_shards : int
            specify the amount of nodes that one write operation in collection is distributed to, thus enhence the capabality of parallel computing potential of Milvus cluster
        metric_type :  MetricType
            the algorithm used to measure similarity among different vectors
        idx_type : IdxType
            the in-memory indexes supported by milvus, which can be configured to achieve better search performance
        **idx_builder : variable keyword arguments
            building parameter(s) specific to the index.

        Returns
        -------
        bool
            indicating whether the collection and partiton are in use successfully
        """ 

        if self.db_name not in db.list_database(using=self._storage_engine):
            db.create_database(db_name=self.db_name, using=self._storage_engine)
        db.using_database(db_name=self.db_name, using=self._storage_engine)

        if not utility.has_collection(collection_name):
            '''
            docstore_id: the generated UUID, the primary key of one memory record
            meta_data_dict: the json dict data, the keys are customized filter conditions, such as category, importance
            description: the embedding vector, which is used to be queried via similarity measuring; can be either floating vector or binary vector
            full_content: the json dict data, the keys some additional content people wish to store, including the plain text of embedded description vector
            '''

            docstore_id = FieldSchema(name='docstore_id', dtype=DataType.INT64, is_primary=True)
            meta_data_dict = FieldSchema(name='meta_data_dict', dtype=DataType.JSON)
            description = FieldSchema(name='description', dtype=DataType.FLOAT_VECTOR, dim=self._embedding_type.dim)
            full_content = FieldSchema(name='full_content', dtype=DataType.JSON)

            coll_schema = CollectionSchema(
                fields=[docstore_id, meta_data_dict, description, full_content]
                )
            
            self.collection = Collection(name=collection_name, schema=coll_schema, using=self._storage_engine, shards_num=num_shards)

        else:
            self.collection = Collection(collection_name)

        # Attach the index to vector field, ie, description Field
        self._search_idx_params = attach_idx(self.collection, 'description', metric_type, False, idx_type, **idx_builder)

        # load the partition in the collection, and use it all the time
        if not self.collection.has_partition(partition_name=self.partition_name):
            self.collection.create_partition(self.partition_name)

        return self.collection is not None # check if the Collection instance and partition has been successfully in use

    def add_memory(
            self, 
            meta_data_dict_list: List[Dict], 
            description_list: List[str], 
            full_content_dict_list: List[str],
            save_time_list: List[str]) -> bool:
        """Insert one or more records into the Milvus database
        
        Parameters
        ----------
        meta_data_dict_list : List[Dict]
            the list of customized filter meta data to be stored in Milvus
        description_list : List[str]
            the list of description sentence to be stored in Milvus
        full_content_dict_list : List[str]
            the list of full content data to be stored in Milvus
        save_time_list : List[str]
            the list of timestamp to be used in the new record

        Returns
        -------
        bool
            indicating whether the records are inserted into Milvus sucessfully
        """ 

        db.using_database(self.db_name, using=self._storage_engine)

        # parameter format check
        if self.collection is None:
            raise Exception('there is no collection in use')
        
        if not (len(meta_data_dict_list) == len(description_list) == len(full_content_dict_list) == len(save_time_list)):
            raise Exception('the list length of each field does not match')
        
        for save_time in save_time_list:
            if not is_valid_timestamp(save_time):
                raise Exception('all elements in save_time_list must follow the format of valid timestamp')
            
        # data field format converting
        doc_id_list = []
        for _ in range(len(meta_data_dict_list)):
            doc_id_list.append(generate_int64_id())

        meta_data_json_list = []
        for meta_data_dict in meta_data_dict_list:
            meta_data_json_list.append(meta_data_dict)

        full_content_json_list = []
        for full_content_dict in full_content_dict_list:
            full_content_json_list.append(full_content_dict)

        description_vector_list = self._get_embedding(description_list)
        
        # Milvus record insertion
        data = [doc_id_list, meta_data_json_list, description_vector_list, full_content_json_list]
        operand = self.collection.insert(data, partition_name=self.partition_name)

        # add the save_time and last_access_time corresponding to certain piece of Milvus data record in mongoDB
        for i in range(len(save_time_list)):
            self.update_attributes(collection_name='milvus_data', attribute_type=str(doc_id_list[i]), key='save_time', value=save_time_list[i])
            self.update_attributes(collection_name='milvus_data', attribute_type=str(doc_id_list[i]), key='last_access_time', value=save_time_list[i])
        
        self.collection.flush()
        return operand.succ_count == len(meta_data_dict_list)

    def search_memory(
            self, 
            query: List[str], 
            current_access_time: str,
            limit: int = 1000,  
            replica_num: int = 1, 
            doc_id_list: Optional[List[int]] = None,
            meta_data_filter: Optional[Dict] = None,) -> List[Dict]:
        """Query up to #limit amount of records that are similar to given query, supporting the filtering using meta_data_dict conditions
        
        Parameters
        ----------
        query : List[str]
            the list of query being used to search from Milvus
        current_access_time : str
            the current timestamp when searching the query
        limit : int
            the maximum amount of records
        replica_num : int
            specify how many query nodes the data will be loaded onto
        doc_id_list : Optional[List[int]]
            optional, the list of specified doc_id, whose attached records are what we want to search from Milvus
        meta_data_filter : Optional[Dict]
            optional, the dict to specify the keys in meta_data_dict to be used and their related filtering descriptions

        Returns
        -------
        List[Dict]
            the memory records that are fetched from Milvus according to query, including three fields: docstore_id, meta_data_dict, full_content
        """ 

        db.using_database(self.db_name, using=self._storage_engine)

        if self.collection is None:
            raise Exception('there is no collection in use')
        
        if not is_valid_timestamp(current_access_time):
            raise Exception('the current access time must follow the format of valid timestamp')
        
        # before doing query, the data must be loaded from disk to memory, as querying is executed in memory
        self.collection.load(partition_names=[self.partition_name] if type(self.partition_name) is str else self.partition_name, replica_number=replica_num)
        
        # form the filter expression
        expr = ''
        if doc_id_list is not None:
            expr += append_expr('docstore_id', 'in ' + str(doc_id_list))

        if meta_data_filter is not None:
            for key, value in meta_data_filter.items():
                expr += append_expr("meta_data_dict['" + key + "']", value)

        expr = expr[:-3]

        # convert query sentence into the embedding vector
        embedded_query = self._get_embedding(query)

        # Milvus records search
        res = self.collection.search(data=embedded_query, anns_field='description', param=self._search_idx_params, limit=limit, expr=expr, 
                                     output_fields=['docstore_id', 'meta_data_dict', 'full_content'])
        
        # handle and process the search results; use set to avoid repetition
        result_data = list()
        visited_doc_ids = set()
        for hits in res:
            for hit in hits:
                docstore_id, meta_data_dict, full_content = hit.entity.get('docstore_id'), hit.entity.get('meta_data_dict'), hit.entity.get('full_content')

                if docstore_id not in visited_doc_ids:
                    # Once several records are successfully searched from Milvus, we need to update their last_access_time in mongoDB
                    self.update_attributes(collection_name='milvus_data', attribute_type=str(docstore_id), key='last_access_time', value=current_access_time)
                    
                    # the processed data, which is provided to user for later usage
                    data = dict()
                    data['doc_id'], data['meta_data_dict'], data['full_content_dict'] = docstore_id, meta_data_dict, full_content
                    result_data.append(data)

                    # set the doc_id as visited one
                    visited_doc_ids.add(docstore_id)

        # after searching the data, it is essential to release them from memory
        self.collection.release()
        return result_data
    
    def filter_memory(
            self, 
            current_access_time: str,
            limit: int = 1000,  
            replica_num: int = 1, 
            doc_id_list: Optional[List[int]] = None,
            meta_data_filter: Optional[Dict] = None,) -> List[Dict]:
        """Filter up to #limit amount of records according to the given conditions
        
        Parameters
        ----------
        current_access_time : str
            the current timestamp when searching the query
        limit : int
            the maximum amount of records
        replica_num : int
            specify how many query nodes the data will be loaded onto
        doc_id_list : Optional[List[int]]
            optional, the list of specified doc_id, whose attached records are what we want to search from Milvus
        **meta_data_filter : Optional[Dict]
            optional, specify the keys in meta_data_dict to be used and their related filtering descriptions

        Returns
        -------
        List[Dict]
            the memory records that are fetched from Milvus according to query, including three fields: docstore_id, meta_data_dict, full_content
        """ 

        db.using_database(self.db_name, using=self._storage_engine)

        if self.collection is None:
            raise Exception('there is no collection in use')
        
        if not is_valid_timestamp(current_access_time):
            raise Exception('the current access time must follow the format of valid timestamp')
        
        # before doing query, the data must be loaded from disk to memory, as querying is executed in memory
        self.collection.load(partition_names=[self.partition_name] if type(self.partition_name) is str else self.partition_name, replica_number=replica_num)
        
        # # form the filter expression
        expr = ''
        if doc_id_list is not None:
            expr += append_expr('docstore_id', 'in ' + str(doc_id_list))

        if meta_data_filter is not None:
            for key, value in meta_data_filter.items():
                expr += append_expr("meta_data_dict['" + key + "']", value)

        expr = expr[:-3]
    
        #expr = "meta_data_dict['importance'] == 8 and meta_data_dict['mood'] in ['extremely happy']"

        #Milvus records search
        res = self.collection.query(expr=expr, limit=limit, output_fields=['docstore_id', 'meta_data_dict', 'full_content'])

        # update the last_access_time for each queried records in Milvus
        for entity in res:
            docstore_id = entity.get('docstore_id')

            # Once several records are successfully searched from Milvus, we need to update their last_access_time in mongoDB
            self.update_attributes(collection_name='milvus_data', attribute_type=str(docstore_id), key='last_access_time', value=current_access_time)

        self.collection.release()
        return res
    
    def delete_memory(
            self, 
            doc_id_list: Optional[List[int]] = None,
            replica_num: int = 1, 
            meta_data_filter: Optional[Dict] = None,) -> int:
        """Delete the filtered records from Milvus
        
        Parameters
        ----------
        doc_id_list : Optional[List[int]]
            optional, the list of specified doc_id, whose attached records are what we want to search from Milvus
        replica_num : int
            specify how many query nodes the data will be loaded onto
        meta_data_filter : Optional[Dict]
            optional, specify the keys in meta_data_dict to be used and their related filtering descriptions

        Returns
        -------
        int
            indicating how many records are successfully deleted from Milvus
        """ 

        db.using_database(self.db_name, using=self._storage_engine)

        if self.collection is None:
            raise Exception('there is no collection in use')
        
        # before doing query, the data must be loaded from disk to memory, as querying is executed in memory
        self.collection.load(partition_names=[self.partition_name] if type(self.partition_name) is str else self.partition_name, replica_number=replica_num)
        
        expr = ''
        if doc_id_list is not None:
            expr += append_expr('docstore_id', 'in ' + str(doc_id_list))

        if meta_data_filter is not None:
            for key, value in meta_data_filter.items():
                expr += append_expr("meta_data_dict['" + key + "']", value)

        expr = expr[:-3]

        #Milvus records search, in here, limit is set to be maxium, ie, 16384
        res = self.collection.query(expr=expr, limit=16384, output_fields=['docstore_id'])

        # Once several records are successfully searched from Milvus, we need to update their last_access_time in mongoDB
        for entity in res:
            self.delete_attribute(collection_name='milvus_data', attribute_type=str(entity.get('docstore_id')))

        operand = self.collection.delete(expr)

        return operand.delete_count
