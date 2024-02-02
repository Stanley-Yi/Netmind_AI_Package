import pytest
from urllib.parse import quote_plus
from xyz.magics.memory.BasicAttributeStorage import BasicAttributeStorage

"""
The unit test case for BasicAttributeStorage class
"""

@pytest.fixture(scope='module')
def collection_bas():
    attribute_storage_name = 'test_attribute_storage'

    # connection informations related to MongoDB
    username = "NetMind"
    password = "NetMindMongoDB"
    escaped_username = quote_plus(username)
    escaped_password = quote_plus(password)

    mongo_url = f"mongodb://{escaped_username}:{escaped_password}@18.171.129.243:27017"

    # initialize the collection-level memory storage unit
    return BasicAttributeStorage(attribute_storage_name, mongo_url)


def test_update_attributes_create(collection_bas):
    result = collection_bas.update_attributes(
        attribute_group_name = "test_collection", 
        attribute_type_name = "Mana", 
        key = "Character_1", 
        value = "Value_1"
    )
    
    assert 'registered_attributes' in collection_bas._mongo_db.list_collection_names()
    assert 'Manaintest_collection' in collection_bas._mongo_db['registered_attributes'].find()[0]['attributes']
    assert result == True


def test_update_attributes_add_new_attribute(collection_bas):
    result = collection_bas.update_attributes(
        attribute_group_name = "test_collection", 
        attribute_type_name = "Bada", 
        key = "Character_1", 
        value = "Value_1"
    )
    
    assert 'Badaintest_collection' in collection_bas._mongo_db['registered_attributes'].find()[0]['attributes']
    assert result == True


def test_update_attributes_add_new_key(collection_bas):
    result = collection_bas.update_attributes(
        attribute_group_name = "test_collection", 
        attribute_type_name = "Bada", 
        key = "Character_2", 
        value = "Value_2"
    )
    
    assert 'Badaintest_collection' in collection_bas._mongo_db['registered_attributes'].find()[0]['attributes']
    assert result == True


def test_update_attributes_modify(collection_bas):
    result = collection_bas.update_attributes(
        attribute_group_name = "test_collection", 
        attribute_type_name = "Bada", 
        key = "Character_1", 
        value = "Value_1_new"
    )
    
    assert 'Badaintest_collection' in collection_bas._mongo_db['registered_attributes'].find()[0]['attributes']
    assert result == True


def test_get_attributes_1(collection_bas):
    result = collection_bas.get_attribute(
        attribute_group_name = "test_collection", 
        attribute_type_name = "Mana", 
        key = "Character_1",
    )
    
    assert result == 'Value_1'


def test_get_attributes_2(collection_bas):
    result = collection_bas.get_attribute(
        attribute_group_name = "test_collection", 
        attribute_type_name = "Bada", 
        key = "Character_1",
    )
    
    assert result == 'Value_1_new'


def test_delete_attribute(collection_bas):
    result = collection_bas.delete_attribute(
        attribute_group_name = "test_collection", 
        attribute_type_name = "Mana", 
    )

    assert 'Manaintest_collection' not in collection_bas._mongo_db['registered_attributes'].find()[0]['attributes']
    assert result == True
    