import pytest
from urllib.parse import quote_plus
from xyz.magics.memory.BasicMemoryMechanism import BasicMemoryMechanism

"""
The unit test case for BasicMemoryMechanism class, specifically test Milvus related methods

add_memory(), search_memory(), filter_memory(), delete_memory()
"""

@pytest.fixture(scope='module')
def collection_bmm() -> BasicMemoryMechanism:
    memory_name = 'test_people_collection'

    # connection informations related to Milvus
    db_name = 'test_milvus_db'
    milvus_host = '18.171.129.243'
    milvus_port = 80
    milvus_user = "root"
    milvus_psw = "NetMindMilvusDB"

    # connection informations related to MongoDB
    username = "NetMind"
    password = "NetMindMongoDB"
    escaped_username = quote_plus(username)
    escaped_password = quote_plus(password)

    mongo_url = f"mongodb://{escaped_username}:{escaped_password}@18.171.129.243:27017"

    # initialize the collection-level memory storage unit
    return BasicMemoryMechanism(
            memory_name=memory_name, 
            db_name=db_name, 
            is_partion_level=False, 
            milvus_host=milvus_host,
            milvus_port=milvus_port,
            milvus_user=milvus_user,
            milvus_psw=milvus_psw,
            mongo_url=mongo_url
            )


@pytest.fixture(scope='module')
def partition_bmm():
    memory_name = 'test_people_partition'

    # connection informations related to Milvus
    db_name = 'test_milvus_db'
    coll_name = 'test_milvus_coll'
    milvus_host = '18.171.129.243'
    milvus_port = 80
    milvus_user = "root"
    milvus_psw = "NetMindMilvusDB"

    # connection informations related to MongoDB
    username = "NetMind"
    password = "NetMindMongoDB"
    escaped_username = quote_plus(username)
    escaped_password = quote_plus(password)

    mongo_url = f"mongodb://{escaped_username}:{escaped_password}@18.171.129.243:27017"

    # initialize the collection-level memory storage unit
    return BasicMemoryMechanism(
            memory_name=memory_name, 
            db_name=db_name, 
            coll_name=coll_name,
            is_partion_level=True, 
            milvus_host=milvus_host,
            milvus_port=milvus_port,
            milvus_user=milvus_user,
            milvus_psw=milvus_psw,
            mongo_url=mongo_url
            )


def test_add_memory_collection(collection_bmm):
    meta_data_dict_list = [{'importance': 10, 'area': 'london', 'mood': 'sad'},
                        {'importance': 8, 'area': 'nottinham', 'mood': 'extremely happy'},
                        {'importance': 2, 'area': 'birmingham', 'mood': 'peaceful'},
                        {'importance': 10, 'area': 'london', 'mood': 'fear'}]

    description_list = ['Eric found that he was rejected by his dream company',
                    'Eric started his first dating activity with a girl',
                    'Eric took the bus to catch system engineering lecture in University of Birmingham as usual',
                    'Eric found that his roommate, Stanley is a gay who want to do something to him']

    full_contents_list = [{'content': 'Eric found that he was rejected by his dream company'},
                      {'content': 'Eric started his first dating activity with a girl'},
                      {'content': 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'},
                      {'content': 'Eric found that his roommate, Stanley is a gay who want to do something to him'}]

    save_time = ['2024-01-09 12:12:53', '2024-02-10 12:12:53', '2024-01-25 12:12:53', '2024-04-01 12:12:53']

    result = collection_bmm.add_memory(meta_data_dict_list, description_list, full_contents_list, save_time)
    assert result == True


def test_add_memory_partition(partition_bmm):
    meta_data_dict_list = [{'importance': 10, 'area': 'london', 'mood': 'sad'},
                        {'importance': 8, 'area': 'nottinham', 'mood': 'extremely happy'},
                        {'importance': 2, 'area': 'birmingham', 'mood': 'peaceful'},
                        {'importance': 10, 'area': 'london', 'mood': 'fear'}]

    description_list = ['Eric found that he was rejected by his dream company',
                    'Eric started his first dating activity with a girl',
                    'Eric took the bus to catch system engineering lecture in University of Birmingham as usual',
                    'Eric found that his roommate, Stanley is a gay who want to do something to him']

    full_contents_list = [{'content': 'Eric found that he was rejected by his dream company'},
                      {'content': 'Eric started his first dating activity with a girl'},
                      {'content': 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'},
                      {'content': 'Eric found that his roommate, Stanley is a gay who want to do something to him'}]

    save_time = ['2024-01-09 12:12:53', '2024-02-10 12:12:53', '2024-01-25 12:12:53', '2024-04-01 12:12:53']

    result = partition_bmm.add_memory(meta_data_dict_list, description_list, full_contents_list, save_time)
    assert result == True


def test_search_memory_collection(collection_bmm):
    query = ['who is Stanley, and what is the relationship between Stanley and Eric?']
    current_access_time = '2024-07-14 09:02:53'
    result = collection_bmm.search_memory(query, current_access_time)[0]
    
    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
    assert meta_dict['importance'] == 10
    assert meta_dict['area'] == 'london'
    assert meta_dict['mood'] == 'fear'

    assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'


def test_search_memory_partition(partition_bmm):
    query = ['who is Stanley, and what is the relationship between Stanley and Eric?']
    current_access_time = '2024-07-14 09:02:53'
    result = partition_bmm.search_memory(query, current_access_time)[0]
    
    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
    assert meta_dict['importance'] == 10
    assert meta_dict['area'] == 'london'
    assert meta_dict['mood'] == 'fear'

    assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'


def test_filter_memory_collection(collection_bmm):
    filter = {'importance': "== 2", 'mood': "in ['peaceful']"}
    current_access_time = '2024-09-14 12:12:53'
    result = collection_bmm.filter_memory(current_access_time, meta_data_filter=filter)[0]

    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content']
    
    assert meta_dict['importance'] == 2
    assert meta_dict['area'] == 'birmingham'
    assert meta_dict['mood'] == 'peaceful'

    assert full_content_dict['content'] == 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'


def test_filter_memory_partition(partition_bmm):
    filter = {'importance': "== 2", 'mood': "in ['peaceful']"}
    current_access_time = '2024-09-01 12:12:53'
    result = partition_bmm.filter_memory(current_access_time, meta_data_filter=filter)[0]

    meta_dict, full_content_dict = result['meta_data_dict'], result['full_content']
    
    assert meta_dict['importance'] == 2
    assert meta_dict['area'] == 'birmingham'
    assert meta_dict['mood'] == 'peaceful'

    assert full_content_dict['content'] == 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'


def test_delete_memory_collection(collection_bmm):
    filter = {'importance': "== 2", 'mood': "in ['peaceful']"}
    result = collection_bmm.delete_memory(meta_data_filter=filter)
    
    assert result == 1


def test_delete_memory_partition(partition_bmm):
    filter = {'importance': "== 2", 'mood': "in ['peaceful']"}
    result = partition_bmm.delete_memory(meta_data_filter=filter)
    
    assert result == 1