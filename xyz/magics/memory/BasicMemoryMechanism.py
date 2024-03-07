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
import traceback
from pymilvus import connections
from typing import Dict, List, Optional, Any
from pymilvus import db, Collection
from pymilvus import utility
from pymilvus import CollectionSchema, FieldSchema, DataType

from xyz.magics.memory.utils import attach_idx, generate_int64_id, is_valid_timestamp, append_expr
from xyz.magics.memory.FilterOperandType import FilterOperand
from xyz.magics.memory._embedding_setting.EmbeddingTypeEnum import EmbeddingType
from xyz.magics.memory._embedding_setting.IdxTypeEnum import IdxType
from xyz.magics.memory._embedding_setting.MetricTypeEnum import MetricType
from xyz.magics.memory.BasicAttributeStorage import BasicAttributeStorage
# from user_settings import client

import os
from openai import OpenAI


class BasicMemoryMechanism:

    def __init__(
            self,
            memory_name: str, 
            db_name: str,
            collection_name: Optional[str] = None,
            partition_name: str = "default",
            if_partion_level: bool = False,
            milvus_host: str = 'localhost', 
            milvus_port: int = 19530, 
            milvus_user: str = 'root',
            milvus_psw: str = 'NetMindMilvusDB',
            mongo_url: Optional[str] = None, 
            # The following parameters always be uesed in default
            storage_engine: Optional[str] = 'default',
            num_shards: Optional[int] = 1,
            embedding_type: Optional[EmbeddingType] = EmbeddingType.OpenAI_text_embedding_ada_002, 
            metric_type: Optional[MetricType] = MetricType.L2, 
            idx_type: Optional[IdxType] = IdxType.IVF_FLAT, 
            **idx_builder):
        """The basic memory object, which has function for modifying memory include saving, loading, retrieving

        Parameters
        ----------
        memory_name : str
            the name of this memory storage
        db_name : str
            the name of used Milvus database
        collection_name : str
            the name of used Milvus collection
        partition_name : str
            the name of used Milvus partition
        if_partion_level : bool
            indicating the type of memory unit storage: true if it is partition-level; false if it is collection-level
        milvus_host : str
            the host of deployed milvus vector database
        milvus_port : str
            the port of deployed milvus vector database
        milvus_user : str
            the user name to log into Milvus vector database
        milvus_psw : str
            the password to log into Milvus vector database
        mongo_url : Optional[str]
            Optional, the url of remote mongo_url, if it is None, then no mongoDB will be binded
        storage_engine : Optional[str]
            Optional, specify in which server the collection is to be created; in Milvus cluster, there can be more than one server, each server will have a server alias
        num_shards : Optional[int]
            Optional, specify the amount of nodes that one write operation in collection is distributed to, thus enhence the capabality of parallel computing potential of Milvus cluster
        embedding_type : Optional[EmbeddingType]
            Optional, the embedding algorithm to be use when embedding the description sentence into a vector
        metric_type : Optional[MetricType]
            Optional, the algorithm used to measure similarity among different vectors
        idx_type : Optional[IdxType]
            Optional, the in-memory indexes supported by milvus, which can be configured to achieve better search performance
        """

        self.client = OpenAI(
            api_key = os.environ.get(
                API_KEY),
        )
        
        self.memory_name = memory_name
        self.collection_name = collection_name
    
        # parameters related to milvus settings
        self._storage_engine = storage_engine
        self.collection = None
        self.db_name = db_name
        self.partition_name = partition_name
        self._search_idx_params = None
        
        # parameters related to embedding
        self._embedding_type = embedding_type
        self.metric_type = metric_type

        self.milvus_connection = { "host": milvus_host, "port": milvus_port, "user": milvus_user, "password": milvus_psw,
                                  "if_partion_level":if_partion_level}
        # Step 1: connect to the Milvus vector database
        try:
            connections.connect(host=milvus_host, port=milvus_port, user=milvus_user, password=milvus_psw)
        except:
            raise Exception('Milvus connect failed: the host or port you provided is not correct')
        
        '''
        The memory records are stored in a single database within Milvus database; 
        each database contains multiple collections; each collections contains multiple partitions; the memory records are actually stored in each partitions
        This BasicMemoryMechanism facilitates two types of memory unit storage levels available, ie, collection-level and partition-level

        - if it is collection-level: The collection is named as collection_name, and all of its memory records are stored in 'default' partition
        - if it is partiton-level: The collection is named as a pre-specified name, and a partition named as partition_name will be created and used within this collection
        '''

        # Step 2: connect to the MongoDB no-SQL database
        self.mongo_db = None
        self.mongo_url = None
        if mongo_url is not None:
            try:
                if self.milvus_connection["if_partion_level"]:
                    self.mongo_db_name = self.partition_name 
                else:
                    self.mongo_db_name = self.collection_name
                self.mongo_db = BasicAttributeStorage(self.mongo_db_name, mongo_url) # connect to mongoDB client, and use the database, whose name is collection_name
                self.mongo_url = mongo_url
            except Exception as e:
                error_message = traceback.format_exc()
                raise Exception (f"MongoDB connect failed: the mongo_url you provided is not correct\n\n{error_message}")
        

        # initialize the collection instance
        if not self._load_memory_store(
                    self.collection_name ,
                    num_shards, 
                    metric_type, 
                    idx_type, 
                    idx_builder=idx_builder):
            raise Exception('loading memory store failed')

    def get_info(self):
        return { 
                "memory_name" : self.memory_name,
                "db_name" : self.db_name, 
                "collection_name" : self.collection_name,
                "partition_name" : self.partition_name,
                "if_partion_level" : self.milvus_connection['if_partion_level'],
                "milvus_host" : self.milvus_connection['host'], 
                "milvus_port" : self.milvus_connection['port'], 
                "milvus_user" : self.milvus_connection['user'], 
                "milvus_psw" : self.milvus_connection['password'], 
                "mongo_url" : self.mongo_url,
                "meta_data" : {
                    "embedding_type" : self._embedding_type,
                    "metric_type" : self.metric_type,
                    }
                }

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
                
                respond = self.client.embeddings.create(
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
            full_content = FieldSchema(name='full_content_dict', dtype=DataType.JSON)

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
    

    def has_mongoDB(self):
        return self.mongo_db is not None
    

    def add_memory(
            self, 
            meta_data_dict_list: List[Dict], 
            description_list: List[str], 
            full_content_dict_list: List[str]) -> bool:
        """Insert one or more records into the Milvus database
        
        Parameters
        ----------
        meta_data_dict_list : List[Dict]
            the list of customized filter meta data to be stored in Milvus
        description_list : List[str]
            the list of description sentence to be stored in Milvus
        full_content_dict_list : List[str]
            the list of full content data to be stored in Milvus

        Returns
        -------
        bool
            indicating whether the records are inserted into Milvus sucessfully
        """ 

        db.using_database(self.db_name, using=self._storage_engine)

        # parameter format check
        if self.collection is None:
            raise Exception('there is no collection in use')
        
        if not (len(meta_data_dict_list) == len(description_list) == len(full_content_dict_list)):
            raise Exception('the list length of each field does not match')
            
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
        
        self.collection.flush()
        return operand.succ_count == len(meta_data_dict_list)

    def search_memory(
            self, 
            query: List[str], 
            advanced_filter: bool = False,
            filter_expression: Optional[str] = None,
            filter_key: Optional[str] = None,
            filter_operand: Optional[FilterOperand] = None,
            filter_value: Optional[Any] = None,
            limit: int = 1000,  
            replica_num: int = 1) -> List[Dict]:
        """Query up to #limit amount of records that are similar to given query, supporting the filtering using meta_data_dict conditions
        
        Parameters
        ----------
        query : List[str]
            the list of query being used to search from Milvus
        advanced_filter : bool
            indicate whether to use advanced filter mode or not; in advanced filter mode, user need to form expr themselves, otherwise filter by only one key in meta_data dict
        filter_expression : Optional[str]
            optional, the expr provided by user, to execute advanced filter]
        filter_key : Optional[str]
            optional, in simple filter mode, specify the key in the meta_data_dict, which is used to filter data
        filter_operand : Optional[FilterOperand]
            optional, in simple filter mode, specify which operand is needed
        filter_value : Optional[Any]
            optional, in simple filter mode, specify the value of filtered data
        limit : int
            the maximum amount of records
        replica_num : int
            specify how many query nodes the data will be loaded onto

        Returns
        -------
        List[Dict]
            the memory records that are fetched from Milvus according to query, including three fields: docstore_id, meta_data_dict, full_content
        """ 

        db.using_database(self.db_name, using=self._storage_engine)

        if self.collection is None:
            raise Exception('there is no collection in use')
        
        if advanced_filter:
            if filter_expression is None:
                raise Exception('In the case of advanced filter, the filter_expression statement must not be None')
            else:
                expr = filter_expression
        else:
            if (filter_key is None or filter_operand is None or filter_value is None):
                expr = None
            else: 
                filter_value = "'" + filter_value + "'" if type(filter_value) == str else str(filter_value)
                filter_key = "meta_data_dict['" + filter_key + "']"
                expr = filter_key + " " + filter_operand.value + " " + filter_value
        
        # before doing query, the data must be loaded from disk to memory, as querying is executed in memory
        self.collection.load(partition_names=[self.partition_name] if type(self.partition_name) is str else self.partition_name, replica_number=replica_num)

        # convert query sentence into the embedding vector
        embedded_query = self._get_embedding(query)

        # Milvus records search
        try:
            res = self.collection.search(data=embedded_query, anns_field='description', param=self._search_idx_params, limit=limit, expr=expr, 
                                     output_fields=['docstore_id', 'meta_data_dict', 'full_content_dict'])
        except:
            raise('There is some error encountered when searching the memory, please do check the filter expression provided')
        
        # handle and process the search results; use set to avoid repetition
        result_data = list()
        visited_doc_ids = set()
        for hits in res:
            for hit in hits:
                docstore_id, meta_data_dict, full_content = hit.entity.get('docstore_id'), hit.entity.get('meta_data_dict'), hit.entity.get('full_content_dict')

                if docstore_id not in visited_doc_ids:
                    
                    # the processed data, which is provided to user for later usage
                    data = dict()
                    data['meta_data_dict'], data['full_content_dict'] = meta_data_dict, full_content
                    result_data.append(data)

                    # set the doc_id as visited one
                    visited_doc_ids.add(docstore_id)

        # after searching the data, it is essential to release them from memory
        self.collection.release()
        return result_data
    
    def filter_memory(
            self, 
            advanced_filter: bool = True,
            filter_expression: Optional[str] = None,
            filter_key: str = None,
            filter_operand: FilterOperand = None,
            filter_value: Any = None,
            limit: int = 1000,  
            replica_num: int = 1, ) -> List[Dict]:
        """Filter up to #limit amount of records according to the given conditions
        
        Parameters
        ----------
        advanced_filter : bool
            indicate whether to use advanced filter mode or not; in advanced filter mode, user need to form expr themselves, otherwise filter by only one key in meta_data dict
        filter_expression : Optional[str]
            optional, the expr provided by user, to execute advanced filter]
        filter_key : Optional[str]
            optional, in simple filter mode, specify the key in the meta_data_dict, which is used to filter data
        filter_operand : Optional[FilterOperand]
            optional, in simple filter mode, specify which operand is needed
        filter_value : Optional[Any]
            optional, in simple filter mode, specify the value of filtered data
        limit : int
            the maximum amount of records
        replica_num : int
            specify how many query nodes the data will be loaded onto

        Returns
        -------
        List[Dict]
            the memory records that are fetched from Milvus according to query, including three fields: docstore_id, meta_data_dict, full_content
        """ 

        db.using_database(self.db_name, using=self._storage_engine)

        if self.collection is None:
            raise Exception('there is no collection in use')
        
        if advanced_filter and filter_expression is None:
            raise Exception('In the case of advanced filter, the filter_expression statement must not be None')
        
        if not advanced_filter and (filter_key is None or filter_operand is None or filter_value is None):
            raise Exception('In the case of non-advanced filter, all of filter_key, filter_operand and filter_value must not be None')
        
        # before doing query, the data must be loaded from disk to memory, as querying is executed in memory
        self.collection.load(partition_names=[self.partition_name] if type(self.partition_name) is str else self.partition_name, replica_number=replica_num)
        
        # form the filter expression
        expr = filter_expression if advanced_filter else ''
        if not advanced_filter:
            filter_value = "'" + filter_value + "'" if type(filter_value) == str else str(filter_value)
            filter_key = "meta_data_dict['" + filter_key + "']"
            expr = filter_key + " " + filter_operand.value + " " + filter_value
    
        #expr = "meta_data_dict['importance'] == 8 and meta_data_dict['mood'] in ['extremely happy']"

        #Milvus records search
        try:
            res = self.collection.query(expr=expr, limit=limit, output_fields=['meta_data_dict', 'full_content_dict'])
        except:
            raise('There is some error encountered when filtering the memory, please do check the filter expression provided')

        self.collection.release()

        return res
    
    def delete_memory(
            self, 
            advanced_filter: bool = True,
            filter_expression: Optional[str] = None,
            filter_key: str = None,
            filter_operand: FilterOperand = None,
            filter_value: Any = None,
            replica_num: int = 1, ) -> int:
        """Delete the filtered records from Milvus
        
        Parameters
        ----------
        advanced_filter : bool
            indicate whether to use advanced filter mode or not; in advanced filter mode, user need to form expr themselves, otherwise filter by only one key in meta_data dict
        filter_expression : Optional[str]
            optional, the expr provided by user, to execute advanced filter]
        filter_key : Optional[str]
            optional, in simple filter mode, specify the key in the meta_data_dict, which is used to filter data
        filter_operand : Optional[FilterOperand]
            optional, in simple filter mode, specify which operand is needed
        filter_value : Optional[Any]
            optional, in simple filter mode, specify the value of filtered data
        replica_num : int
            specify how many query nodes the data will be loaded onto

        Returns
        -------
        int
            indicating how many records are successfully deleted from Milvus
        """ 

        db.using_database(self.db_name, using=self._storage_engine)

        if self.collection is None:
            raise Exception('there is no collection in use')
        
        if advanced_filter and filter_expression is None:
            raise Exception('In the case of advanced filter, the filter_expression statement must not be None')
        
        if not advanced_filter and (filter_key is None or filter_operand is None or filter_value is None):
            raise Exception('In the case of non-advanced filter, all of filter_key, filter_operand and filter_value must not be None')
        
        # before doing query, the data must be loaded from disk to memory, as querying is executed in memory
        self.collection.load(partition_names=[self.partition_name] if type(self.partition_name) is str else self.partition_name, replica_number=replica_num)
        
        # form the filter expression
        expr = filter_expression if advanced_filter else ''
        if not advanced_filter:
            filter_value = "'" + filter_value + "'" if type(filter_value) == str else str(filter_value)
            filter_key = "meta_data_dict['" + filter_key + "']"
            expr = filter_key + " " + filter_operand.value + " " + filter_value

        operand = self.collection.delete(expr)

        return operand.delete_count
