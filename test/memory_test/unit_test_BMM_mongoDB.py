import pytest
from urllib.parse import quote_plus
from xyz.magics.memory.BasicMemoryMechanism import BasicMemoryMechanism

"""
The unit test case for BasicMemoryMechanism class, specifically test MongoDB related methods

update_attributes(), get_attribute(), delete_attribute()
"""

@pytest.fixture(scope='module')
def collection_bmm():
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


def test_update_attributes_create(collection_bmm):
    result = collection_bmm.update_attributes(
        collection_name = "test_collection", 
        attribute_type = "Mana", 
        key = "Character_1", 
        value = "Value_1"
    )
    
    assert 'registered_attributes' in collection_bmm._mongo_db.list_collection_names()
    assert 'Manaintest_collection' in collection_bmm._mongo_db['registered_attributes'].find()[0]['attributes']
    assert result == True


def test_update_attributes_add_new_attribute(collection_bmm):
    result = collection_bmm.update_attributes(
        collection_name = "test_collection", 
        attribute_type = "Bada", 
        key = "Character_1", 
        value = "Value_1"
    )
    
    assert 'Badaintest_collection' in collection_bmm._mongo_db['registered_attributes'].find()[0]['attributes']
    assert result == True


def test_update_attributes_add_new_key(collection_bmm):
    result = collection_bmm.update_attributes(
        collection_name = "test_collection", 
        attribute_type = "Bada", 
        key = "Character_2", 
        value = "Value_2"
    )
    
    assert 'Badaintest_collection' in collection_bmm._mongo_db['registered_attributes'].find()[0]['attributes']
    assert result == True


def test_update_attributes_modify(collection_bmm):
    result = collection_bmm.update_attributes(
        collection_name = "test_collection", 
        attribute_type = "Bada", 
        key = "Character_1", 
        value = "Value_1_new"
    )
    
    assert 'Badaintest_collection' in collection_bmm._mongo_db['registered_attributes'].find()[0]['attributes']
    assert result == True


def test_get_attributes_1(collection_bmm):
    result = collection_bmm.get_attribute(
        collection_name = "test_collection", 
        attribute_type = "Mana", 
        key = "Character_1",
    )
    
    assert result == 'Value_1'


def test_get_attributes_2(collection_bmm):
    result = collection_bmm.get_attribute(
        collection_name = "test_collection", 
        attribute_type = "Bada", 
        key = "Character_1",
    )
    
    assert result == 'Value_1_new'


def test_delete_attribute(collection_bmm):
    result = collection_bmm.delete_attribute(
        collection_name = "test_collection", 
        attribute_type = "Mana", 
    )

    assert 'Manaintest_collection' not in collection_bmm._mongo_db['registered_attributes'].find()[0]['attributes']
    assert result == True