import pytest
from urllib.parse import quote_plus
from xyz.magics.memory.BasicMemorySet import BasicMemorySet


@pytest.fixture(scope='module')
def collection_bmm() -> BasicMemorySet:
    
    config_json_path = "test/memory_test/test_info.json"
    # initialize the collection-level memory storage unit
    return BasicMemorySet(
            info_path=config_json_path, 
            db_name="test_db"
            )
    
def test_connect_memory(collection_bmm):
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

    result = collection_bmm.memory["test_memory"].add_memory(meta_data_dict_list, description_list, full_contents_list, save_time)
    assert result == True
    
    
    
    