from pymongo import MongoClient
from typing import Any


class BasicAttributeStorage():
    
    def __init__(
            self,
            attribute_storage_name: str,
            mongo_url: str = 'mongodb://localhost:27017/'):
        """The basic pure-attribute storage object, which has function for modifying attribute dict include updating, getting and deleting

        Parameters
        ----------
        attribute_storage_name : str
            the name of this attribute storage
        mongo_url : str
            the url of deployed mongoDB server
        """
        
        # Connect to the MongoDB no-SQL database
        self._mongo_db = None
        self.mongo_url = mongo_url
        self.attribute_storage_name = attribute_storage_name
        try:
            client = MongoClient(self.mongo_url)
            self._mongo_db = client[self.attribute_storage_name] # connect to mongoDB client, and use the database, whose name is attribute_group_name
        except Exception as e:
            raise Exception('Milvus connect failed: the host or port you provided is not correct')
        
        '''
        The info format of registered_attributes related to a single memory unit is:

        In database - attribute_storage_name:
        In collection - 'registered_attributes':
        [
            {
                ''attributes'': list(),
            }
        ]
        '''

        '''
        The format of attribute dict related to a single attribute storage is:

        In database - attribute_storage_name:
        In collection - attribute_group_1:
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

    def get_info(self):
        return {
            self.attribute_storage_name,
            self.mongo_url
        }
    
    def update_attributes(
            self, 
            attribute_group_name: str, 
            attribute_type_name: str, 
            key: str, 
            value: Any) -> bool:
        """Insert or update the attribute value into mongoDB

        Parameters
        ----------
        attribute_group_name : str
            the name of collection, in which certain group of documents is stored
        attribute_type_name : str
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

        registered = attribute_type_name + 'in' + attribute_group_name

        if registered not in registered_attributes:
            # if the attribute_type is not registered, do the insertion; and register the new attribute_type to the mongoDB
            data = {}
            data['attribute_type'] = attribute_type_name
            data['values'] = {key: value}
            operation_1 = self._mongo_db[attribute_group_name].insert_one(data)

            registered_attributes.append(registered)
            operation_2 = self._mongo_db['registered_attributes'].update_one(filter=old_registered_value, update={'$set': {'attributes': registered_attributes}})

            return operation_1.inserted_id is not None and operation_2.modified_count == 1
        else:
            # if the attribut_type is registered, get the full origin json data mapped to key 'values', and do the update
            values_json = self._mongo_db[attribute_group_name].find_one({'attribute_type': attribute_type_name})['values'].copy()
            values_json[key] = value

            operation = self._mongo_db[attribute_group_name].update_one(filter={'attribute_type': attribute_type_name}, update={'$set': {'values': values_json}})

            return operation.modified_count == 1

    def get_attribute(
            self, 
            attribute_group_name: str, 
            attribute_type_name: str, 
            key: str) -> Any:
        """Get the attribute value from mongoDB

        Parameters
        ----------
        attribute_group_name : str
            the name of collection, in which certain group of documents is stored
        attribut_type_name : str
            the type of attribute, which is corresponding to a set of different key-value properties
        key : str
            the name of key, which is used to select value from key-value properties that is corresponding to given attribute_type

        Returns
        -------
        Any
            depends on the type of fetched value
       """
        if 'registered_attributes' not in self._mongo_db.list_collection_names():
            raise Exception('Currently there is no attributes registered yet')
        
        registered_attributes = self._mongo_db['registered_attributes'].find()[0]['attributes']
        registered = attribute_type_name + 'in' + attribute_group_name

        if registered not in registered_attributes:
            raise Exception('the specified attribute_type does not exist')

        values_json = self._mongo_db[attribute_group_name].find_one({'attribute_type': attribute_type_name})['values']

        try:
            return values_json[key]
        except KeyError:
            raise Exception('the specified key does not exist, or does not belong to given attribute type')

    def delete_attribute(
            self, 
            attribute_group_name: str, 
            attribute_type_name: str) -> bool:
        """Delete the document related to given attribute_type from mongoDB

        Parameters
        ----------
        attribute_group_name : str
            the name of collection, in which certain group of documents is stored
        attribut_type_name : str
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
        registered = attribute_type_name + 'in' + attribute_group_name

        if registered not in registered_attributes:
            raise Exception('the specified attribute_type does not exist')

        operation_1 = self._mongo_db[attribute_group_name].delete_one({'attribute_type': attribute_type_name})
        
        registered_attributes = registered_attributes
        registered_attributes.remove(registered)
        operation_2 = self._mongo_db['registered_attributes'].update_one(filter=old_registered_value, update={'$set': {'attributes': registered_attributes}})

        return operation_1.deleted_count == 1 and operation_2.modified_count == 1