import pytest
from urllib.parse import quote_plus
from xyz.magics.memory.BasicMemoryMechanism import BasicMemoryMechanism
from xyz.magics.memory.FilterOperandType import FilterOperand

"""
The unit test case for BasicMemoryMechanism class, specifically test Milvus related methods

add_memory(), search_memory(), filter_memory(), delete_memory()

Since the collection-level and partition-level shares the same operation on above methods, 
the partiton-level tests has been comment out; you can remove the comment and run test as you wish
"""

@pytest.fixture(scope='module')
def collection_bmm() -> BasicMemoryMechanism:
    """
    create the collection-level memory mechanism object, and connect to remote Milvus database
    """

    memory_name = 'test_people_collection_1'

    # connection informations related to Milvus
    db_name = 'test_milvus_db_12341'
    milvus_host = '18.171.129.243'
    milvus_port = 80
    milvus_user = "root"
    milvus_psw = "NetMindMilvusDB"

    # connection informations related to MongoDB
    # NOTE: if you do not want to use mongoDB, you can just set the mongo_url to None
    username = "NetMind"
    password = "NetMindMongoDB"
    escaped_username = quote_plus(username)
    escaped_password = quote_plus(password)

    mongo_url = f"mongodb://{escaped_username}:{escaped_password}@18.171.129.243:27017"

    # initialize the collection-level memory storage unit
    return BasicMemoryMechanism(
            memory_name=memory_name, 
            db_name=db_name, 
            collection_name=memory_name,
            if_partion_level=False, 
            milvus_host=milvus_host,
            milvus_port=milvus_port,
            milvus_user=milvus_user,
            milvus_psw=milvus_psw,
            mongo_url=mongo_url
            )


@pytest.fixture(scope='module')
def partition_bmm():
    """
    create the partition-level memory mechanism object, and connect to remote Milvus database
    """
        
    memory_name = 'test_people_partition_1'

    # connection informations related to Milvus
    db_name = 'test_milvus_db_12341'
    coll_name = 'test_milvus_coll'
    partition_name = 'test_people_partition'
    milvus_host = '18.171.129.243'
    milvus_port = 80
    milvus_user = "root"
    milvus_psw = "NetMindMilvusDB"

    # connection informations related to MongoDB
    # NOTE: if you do not want to use mongoDB, you can just set the mongo_url to None
    username = "NetMind"
    password = "NetMindMongoDB"
    escaped_username = quote_plus(username)
    escaped_password = quote_plus(password)

    mongo_url = f"mongodb://{escaped_username}:{escaped_password}@18.171.129.243:27017"

    # initialize the collection-level memory storage unit
    return BasicMemoryMechanism(
            memory_name=memory_name, 
            db_name=db_name, 
            collection_name=coll_name,
            partition_name=partition_name,
            if_partion_level=True, 
            milvus_host=milvus_host,
            milvus_port=milvus_port,
            milvus_user=milvus_user,
            milvus_psw=milvus_psw,
            mongo_url=mongo_url,
            )


def test_add_memory_collection(collection_bmm):
    """
    Add a batch of memories into the memory mechanism
    """

    # the meta_data_dict_list contains a list k-v data, which will be used to filter the memories
    meta_data_dict_list = [{'importance': 10, 'area': 'london', 'mood': 'sad'},
                        {'importance': 8, 'area': 'nottinham', 'mood': 'extremely happy'},
                        {'importance': 2, 'area': 'birmingham', 'mood': 'peaceful'},
                        {'importance': 10, 'area': 'london', 'mood': 'fear'}]

    # the description_list contains a list of strings, which will be embedded and stored, used to queried according to similarity
    description_list = ['Eric found that he was rejected by his dream company',
                    'Eric started his first dating activity with a girl',
                    'Eric took the bus to catch system engineering lecture in University of Birmingham as usual',
                    'Eric found that his roommate, Stanley is a gay who want to do something to him']

    # the full_content_list contains a list of k-v data, whcih is the real contents needed to be stored and used in application
    full_contents_list = [{'content': 'Eric found that he was rejected by his dream company'},
                      {'content': 'Eric started his first dating activity with a girl'},
                      {'content': 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'},
                      {'content': 'Eric found that his roommate, Stanley is a gay who want to do something to him'}]

    # the returned result of add_memory indicate whether this batch of memory inserted successfully
    result = collection_bmm.add_memory(meta_data_dict_list, description_list, full_contents_list)
    assert result == True


def test_search_memory_collection_simple(collection_bmm):
    """
    Given a list of query sentences, search the related memories out from the memory mechanism

    In addition to query sentences, we also demonstrate the use case of simple filter mode, 
    which is useful when you only want to compare the value of a single key in meta_data_dict with target value
    """

    # the query sentence shall be in a list, even if there is only one sentence
    query = ['who is Stanley, and what is the relationship between Stanley and Eric?']

    # the key in meta_data_dict to be filtered
    filter_key = 'importance'

    # the operand of comparison, enumerate value
    filter_operand = FilterOperand.GREATER_OR_EQUAL

    # the target value
    filter_value = 7

    # the returned result is a list of dict, containing two keys: meta_data_dict and full_content_dict
    result = collection_bmm.search_memory(query, 
                                          advanced_filter=False, 
                                          filter_key=filter_key,
                                          filter_operand=filter_operand,
                                          filter_value=filter_value)[0]
    
    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
    assert meta_dict['importance'] == 10
    assert meta_dict['area'] == 'london'
    assert meta_dict['mood'] == 'fear'

    assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'


def test_search_memory_collection_advanced(collection_bmm):
    """
    Given a list of query sentences, search the related memories out from the memory mechanism

    In addition to query sentences, we also demonstrate the use case of advanced filter mode, 
    which is useful when you want to compare multiple keys in meta_data_dict at once
    
    for more details about forming the expr, please check out https://milvus.io/docs/boolean.md
    """

    query = ['who is Stanley, and what is the relationship between Stanley and Eric?']
    expr = "meta_data_dict['mood'] == 'fear' && meta_data_dict['importance'] == 10"
    result = collection_bmm.search_memory(query, 
                                          advanced_filter=True, 
                                          filter_expression = expr)[0]
    
    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
    assert meta_dict['importance'] == 10
    assert meta_dict['area'] == 'london'
    assert meta_dict['mood'] == 'fear'

    assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'


def test_search_memory_collection_empty(collection_bmm):
    """
    Given a list of query sentences, search the related memories out from the memory mechanism

    In addition to query sentences, we also demonstrate the use case of without any meta_data filtering
    which is useful when you only want to fetch out memories that are related to query sentences
    """

    query = ['who is Stanley, and what is the relationship between Stanley and Eric?']
    expr = ""
    result = collection_bmm.search_memory(query, 
                                          advanced_filter=True, 
                                          filter_expression = expr)[0]
    
    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
    assert meta_dict['importance'] == 10
    assert meta_dict['area'] == 'london'
    assert meta_dict['mood'] == 'fear'

    assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'


def test_filter_memory_collection_simple(collection_bmm):
    """
    filter the memories from memory mechanism based on meta_data_dict, in simple filter mode
    """

    filter_key = 'importance'
    filter_operand = FilterOperand.LESS_OR_EQUAL
    filter_value = 5
    result = collection_bmm.filter_memory(advanced_filter=False, 
                                            filter_key=filter_key,
                                            filter_operand=filter_operand,
                                            filter_value=filter_value)[0]
    
    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
    assert meta_dict['importance'] == 2
    assert meta_dict['area'] == 'birmingham'
    assert meta_dict['mood'] == 'peaceful'

    assert full_content_dict['content'] == 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'


def test_filter_memory_collection_advanced(collection_bmm):
    """
    filter the memories from memory mechanism based on meta_data_dict, in advanced filter mode

    for more details about forming the expr, please check out https://milvus.io/docs/boolean.md
    """

    expr = "meta_data_dict['mood'] == 'fear' && meta_data_dict['importance'] == 10"
    result = collection_bmm.filter_memory(advanced_filter=True, 
                                          filter_expression = expr)[0]
    
    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
    assert meta_dict['importance'] == 10
    assert meta_dict['area'] == 'london'
    assert meta_dict['mood'] == 'fear'

    assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'


def test_filter_memory_collection_empty(collection_bmm):
    """
    filter out all memories from memory mechanism
    """

    expr = ""
    result = collection_bmm.filter_memory(advanced_filter=True, 
                                          filter_expression = expr)
    
    assert len(result) == 4


def test_delete_memory_collection_simple(collection_bmm):
    """
    delete the memories from memory mechanism based on meta_data_dict, in simple filter mode
    """

    filter_key = 'mood'
    filter_operand = FilterOperand.EQUAL_TO
    filter_value = 'fear'
    result = collection_bmm.delete_memory(advanced_filter=False,
                                          filter_key=filter_key,
                                          filter_operand=filter_operand,
                                          filter_value=filter_value)
    
    assert result == 1


def test_delete_memory_collection_advanced(collection_bmm):
    """
    delete the memories from memory mechanism based on meta_data_dict, in advanced filter mode

    for more details about forming the expr, please check out https://milvus.io/docs/boolean.md
    """

    expr = "meta_data_dict['mood'] == 'fear' && meta_data_dict['importance'] == 10"
    result = collection_bmm.delete_memory(advanced_filter=True,
                                          filter_expression=expr)
    
    assert result == 0


def test_delete_memory_collection_all(collection_bmm):
    """
    delete all memories from memory mechanism
    """

    expr = "meta_data_dict['importance'] > 0"
    result = collection_bmm.delete_memory(advanced_filter=True,
                                filter_expression=expr)
    
    assert result == 3

"""
def test_add_memory_partition(partition_bmm):
        
    # the meta_data_dict_list contains a list k-v data, which will be used to filter the memories
    meta_data_dict_list = [{'importance': 10, 'area': 'london', 'mood': 'sad'},
                        {'importance': 8, 'area': 'nottinham', 'mood': 'extremely happy'},
                        {'importance': 2, 'area': 'birmingham', 'mood': 'peaceful'},
                        {'importance': 10, 'area': 'london', 'mood': 'fear'}]

    # the description_list contains a list of strings, which will be embedded and stored, used to queried according to similarity
    description_list = ['Eric found that he was rejected by his dream company',
                    'Eric started his first dating activity with a girl',
                    'Eric took the bus to catch system engineering lecture in University of Birmingham as usual',
                    'Eric found that his roommate, Stanley is a gay who want to do something to him']

    # the full_content_list contains a list of k-v data, whcih is the real contents needed to be stored and used in application
    full_contents_list = [{'content': 'Eric found that he was rejected by his dream company'},
                      {'content': 'Eric started his first dating activity with a girl'},
                      {'content': 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'},
                      {'content': 'Eric found that his roommate, Stanley is a gay who want to do something to him'}]

    # the returned result of add_memory indicate whether this batch of memory inserted successfully
    result = partition_bmm.add_memory(meta_data_dict_list, description_list, full_contents_list)
    assert result == True

    
def test_search_memory_partition_simple(partition_bmm):
    query = ['who is Stanley, and what is the relationship between Stanley and Eric?']
    filter_key = 'importance'
    filter_operand = FilterOperand.GREATER_OR_EQUAL
    filter_value = 7
    result = partition_bmm.search_memory(query, 
                                          advanced_filter=False, 
                                          filter_key=filter_key,
                                          filter_operand=filter_operand,
                                          filter_value=filter_value)[0]
    
    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
    assert meta_dict['importance'] == 10
    assert meta_dict['area'] == 'london'
    assert meta_dict['mood'] == 'fear'

    assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'


def test_search_memory_partition_advanced(partition_bmm):
    query = ['who is Stanley, and what is the relationship between Stanley and Eric?']
    expr = "meta_data_dict['mood'] == 'fear' && meta_data_dict['importance'] >= 10"
    result = partition_bmm.search_memory(query, 
                                          advanced_filter=True, 
                                          filter_expression = expr)[0]
    
    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
    assert meta_dict['importance'] == 10
    assert meta_dict['area'] == 'london'
    assert meta_dict['mood'] == 'fear'

    assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'


def test_search_memory_partition_empty(partition_bmm):
    query = ['who is Stanley, and what is the relationship between Stanley and Eric?']
    expr = ""
    result = partition_bmm.search_memory(query, 
                                          advanced_filter=True, 
                                          filter_expression = expr)[0]
    
    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
    assert meta_dict['importance'] == 10
    assert meta_dict['area'] == 'london'
    assert meta_dict['mood'] == 'fear'

    assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'

    
def test_filter_memory_partititon_simple(partition_bmm):
    filter_key = 'importance'
    filter_operand = FilterOperand.LESS_OR_EQUAL
    filter_value = 5
    result = partition_bmm.filter_memory(advanced_filter=False, 
                                            filter_key=filter_key,
                                            filter_operand=filter_operand,
                                            filter_value=filter_value)[0]
    
    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
    assert meta_dict['importance'] == 2
    assert meta_dict['area'] == 'birmingham'
    assert meta_dict['mood'] == 'peaceful'

    assert full_content_dict['content'] == 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'


def test_filter_memory_partition_advanced(partition_bmm):
    expr = "meta_data_dict['mood'] == 'fear' && meta_data_dict['importance'] == 10"
    result = partition_bmm.filter_memory(advanced_filter=True, 
                                          filter_expression = expr)[0]
    
    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
    assert meta_dict['importance'] == 10
    assert meta_dict['area'] == 'london'
    assert meta_dict['mood'] == 'fear'

    assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'


def test_filter_memory_partition_empty(partition_bmm):
    expr = ""
    result = partition_bmm.filter_memory(advanced_filter=True, 
                                          filter_expression = expr)
    
    assert len(result) == 4

    
def test_delete_memory_partition_simple(partition_bmm):
    filter_key = 'mood'
    filter_operand = FilterOperand.EQUAL_TO
    filter_value = 'fear'
    result = partition_bmm.delete_memory(advanced_filter=False,
                                          filter_key=filter_key,
                                          filter_operand=filter_operand,
                                          filter_value=filter_value)
    
    assert result == 1


def test_delete_memory_partiton_advanced(partition_bmm):
    expr = "meta_data_dict['mood'] == 'fear' && meta_data_dict['importance'] == 10"
    result = partition_bmm.delete_memory(advanced_filter=True,
                                          filter_expression=expr)
    
    assert result == 0

    
def test_delete_memory_partition_all(partition_bmm):
    expr = "meta_data_dict['importance'] > 0"
    result = partition_bmm.delete_memory(advanced_filter=True,
                                filter_expression=expr)
    
    assert result == 4
"""