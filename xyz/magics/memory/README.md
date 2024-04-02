## Memory (NetMind.AI-XYZ)

本文档不是正式文档，只是为了方便 team 内部沟通，进行编写的。
Author: BlackSheep-Team

### 文件介绍：

```bash
memory
├── _embedding_setting
│   ├── EmbeddingTypeEnum.py
│   ├── IdxTypeEnum.py
│   ├── __init__.py
│   └── MetricTypeEnum.py
├── __init__.py
├── BasicAttributeStorage.py
├── BasicMemoryMechanism.py
├── MemoryAgent.py
├── memory_client.py
├── _memory_config_template.py
├── README.md
└── pai_company_utils.py
```

Group 1:
`_embedding_setting/*`, `BasicAttributeStorage.py`, `BasicMemoryMechanism.py`
我们利用这些 python 脚本，实现了最基础的 Milvus 向量数据库或者 MongoDB。
我们可一利用这些实例化对象 `BasicAttributeStorage, BasicMemoryMechanism` 对数据库进行 增删改查。

Group 2:
`MemoryClient.py`, `MemoryAgent.py`
在实际项目中我们用到的接口：
`MemoryClient` 在一个项目中起到与服务连接的能力，独例模式，在一个项目的 runtime 中只有一个实例化对象。
MemoryAgent` 在一个项目中会有许多个不同的实例化对象，本身并不与服务器上的database进行连接，而是通过 Client 进行连接。
好处是：不需要每个 Agent 都单独和远程服务创建连接。（这一点需要 Zhouhan 进行确认，是不是我们想要的这种形式。）

一些必要的说明：
1. 连接数据库的时候，建议使用 `MemoryAgent` 根据 config 进行连接。如果那台服务器上有要链接的数据库，就会自动连接；如果没有，则根据 `db_name, collection_name, partition_name` 去创建。
2. config 用例 请看 `test/memory_test/unit_test_client.py` 文件和 `BasicMemoryMechanism.py`的构造函数。
3. 一个数据库要根据 `db_name, collection_name, partition_name` 去确定。 `memory_name` 只是我们用来给他起名用的，但是建议和 `collection_name` 或 `partition_name` 其中一个相等。 
4. 项目还在完善中，有更优雅的方式请尽管使用。
4. 可以对已有函数、方法、对象进行修改，但是要保证 所有的 test 文件能够顺利全部通过。

快速熟悉代码的方式：
1. 阅读代码：`BasicAttributeStorage.py`, `BasicMemoryMechanism.py`，`MemoryClient.py`, `MemoryAgent.py` 所有的功能内容都写在 docstring 里了。
2. 沟通，
   1. Zhouhan Zhang: `BasicAttributeStorage.py`, `BasicMemoryMechanism.py`
   2. Tianlei: 部署于 AWS EC2
   3. Bin Liang: `MemoryClient.py`, `MemoryAgent.py`
3. 看 test 文件，`NetMind_AI_XYZ/test/memory_test`.
   
    client_config 主要参数的说明:
     - `collection_name`: collection_name用于标识向量数据库中的一个collection. 一个collection通常用来存储一个agent的一类数据, 比如存储一个agent 的某一类知识. 一个collection 中每条数据需要有相同的metadata.
     - `partition_name`: partition_name 用于标识一个 collection 的子集. 一个collection 中的partition数量是有限的, 使用 partition 主要用于在collection的子集中做检索, 一个 collection 中不同partition有相同的metadata.
     - `db_name`: db_name 用来标识一个向量数据库的服务. 一个db_name有多个 collection, 不同collection可以有不同的metadata.
     - `memory_name`: 一个agent可能有多个collection, memory_name 用于在逻辑上区分一个agent的不同知识库或记忆库.

### 目前进展

#### Marketing 需求

经过和 He Yan 确认，我们目前的 client、agent 结构已经能够满足 Marketing 项目的需求。

#### 复杂 retrieval 方式开发

开发形式（暂定）：
1. 建立新的 branch
2. 在独立的 branch 内开发
3. 使用 PEP8 的规范，docstring用 numpy style。
   1. Class 命名：驼峰命名法
   2. 变量 命名：下划线命名法
   3. 命名尽量不要使用缩写
4. 对于 整个 memory 文件夹内的所有内容 都可以根据自己的需求进行增加或者修改。

目前目标：

1. 结构化搜索
2. 联想

以下内容仅仅是参考：
这两个功能都应该在 `MemoryAgent` 内部进行开发。

`MemoryAgent.structured_search(Chain, query)`:
1. MemoryAgent 有这个对象方法。
   1. 可以是多种形式，我只是打个比方，比如 
      1. `MemoryAgent.create_chain()`
      2. `MemoryAgent.chain["xxx"].search(quert)`
2. 定义 Chain 这个对象的形式。
   1. 如何创建这个对象，内部包含一个 类似TF.sequential() 的内容。
   2. 需要实现 Knowledge 1 -> Agent input -> Agent output -> Knowledge 2 -> ...

`MemoryAgent.associate(query)`
1. 比如，可以在指定步数内，重复 搜索、agent 处理、搜索....这个过程。
2. 重点是，在每一次 当前信息内容、信息量发生变化的时候，可以自行选择 下一个要去搜索的知识库是什么。

## Import all essential packages

```python
from xyz.magics.memory.BasicMemoryMechanism import BasicMemoryMechanism 
from xyz.magics.memory.BasicAttributeStorage import BasicAttributeStorage
```

## BasicAttributeStorage

The basic pure-attribute storage object, which has function for modifying attribute dict include updating, getting and deleting

### 1 - Initialize the BasicAttributeStorage instance

```python
attribute_storage_name = 'test_attribute_storage'

# connection informations related to MongoDB
username = "NetMind"
password = "NetMindMongoDB"
escaped_username = quote_plus(username)
escaped_password = quote_plus(password)

mongo_url = f"mongodb://{escaped_username}:{escaped_password}@18.171.129.243:27017"

# initialize the BasicAttributeStorage instance
bas = BasicAttributeStorage(attribute_storage_name, mongo_url)
```

| Parameter                | Type     | Default                        | Description                                                             |
|--------------------------|----------|--------------------------------|-------------------------------------------------------------------------|
| `attribute_storage_name` | `str`    |                                | The name of this attribute storage.                                     |
| `mongo_url`              | `str`    | `"mongodb://localhost:27017/"` | The URL of the deployed MongoDB server.                                 |

**Purpose:** Initializes the basic pure-attribute storage object with specified configurations for attribute management operations.

### 2 - Insert or update the attribute value into mongoDB

```python
result = bas.update_attributes(
        attribute_group_name = "test_collection", 
        attribute_type_name = "Mana", 
        key = "Character_1", 
        value = "Value_1"
    )
    
assert 'registered_attributes' in bas._mongo_db.list_collection_names()
assert 'Manaintest_collection' in bas._mongo_db['registered_attributes'].find()[0]['attributes']
assert result == True
```

| Parameter              | Type      | Default | Description                                                                                                    |
|------------------------|-----------|---------|----------------------------------------------------------------------------------------------------------------|
| `attribute_group_name` | `str`     |         | The name of the collection in which a certain group of documents is stored.                                    |
| `attribute_type_name`  | `str`     |         | The type of attribute, corresponding to a set of different key-value properties.                               |
| `key`                  | `str`     |         | The name of the key, used to select a value from key-value properties corresponding to the given attribute type. |
| `value`                | `Any`     |         | The new value to be stored; the type depends on the given value.                                               |

**Returns:** `bool` - Indicates whether the new value is inserted into MongoDB successfully.


### 3 - Get the attribute value from mongoDB

```python
result = bas.get_attribute(
        attribute_group_name = "test_collection", 
        attribute_type_name = "Mana", 
        key = "Character_1",
    )
    
assert result == 'Value_1'
```

| Parameter              | Type  | Default | Description                                                                                                     |
|------------------------|-------|---------|-----------------------------------------------------------------------------------------------------------------|
| `attribute_group_name` | `str` |         | The name of the collection in which a certain group of documents is stored.                                     |
| `attribute_type_name`  | `str` |         | The type of attribute, corresponding to a set of different key-value properties.                                |
| `key`                  | `str` |         | The name of the key, used to select a value from key-value properties corresponding to the given attribute type. |

**Returns:** `Any` - The type of the fetched value depends on the stored data.


### 4 - Delete the document related to given attribute_type from mongoDB

```python
result = collection_bas.delete_attribute(
        attribute_group_name = "test_collection", 
        attribute_type_name = "Mana", 
    )

assert 'Manaintest_collection' not in collection_bas._mongo_db['registered_attributes'].find()[0]['attributes']
assert result == True
```

| Parameter              | Type  | Default | Description                                                                                                  |
|------------------------|-------|---------|--------------------------------------------------------------------------------------------------------------|
| `attribute_group_name` | `str` |         | The name of the collection in which a certain group of documents is stored.                                  |
| `attribute_type_name`  | `str` |         | The type of attribute, corresponding to a set of different key-value properties.                             |

**Returns:** `bool` - Indicates whether the documents were successfully deleted from MongoDB.



## BasicMemoryMechanism

The BasicMemoryMechanism is the basic memory object, which has function for modifying memory include saving, loading, retrieving

### 1 - Initialize the BasicMemoryMechanism Instance

```python
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
bmm =  BasicMemoryMechanism(
            memory_name=memory_name, 
            db_name=db_name, 
            collection_name=memory_name,
            is_partion_level=False, 
            milvus_host=milvus_host,
            milvus_port=milvus_port,
            milvus_user=milvus_user,
            milvus_psw=milvus_psw,
            mongo_url=mongo_url
            )
```


| Parameter          | Type            | Default                        | Description                                                                                                           |
|--------------------|-----------------|--------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| `memory_name`      | `str`           |                                | The name of this memory storage.                                                                                      |
| `db_name`          | `str`           |                                | The name of the used Milvus database.                                                                                 |
| `collection_name`  | `str`           | `None`                         | The name of the used Milvus collection.                                                                               |
| `partition_name`   | `str`           | `"default"`                    |  The name of the used Milvus partition within the given collection                                                                                                                     |
| `if_partition_level` | `bool`        | `False`                        | Indicating the type of memory unit storage: true if it is partition-level; false if it is collection-level.           |
| `milvus_host`      | `str`           | `"localhost"`                  | The host of the deployed Milvus vector database.                                                                      |
| `milvus_port`      | `int`           | `19530`                        | The port of the deployed Milvus vector database.                                                                      |
| `milvus_user`      | `str`           | `"root"`                       | The user name to log into the Milvus vector database.                                                                 |
| `milvus_psw`       | `str`           | `"NetMindMilvusDB"`            | The password to log into the Milvus vector database.                                                                  |
| `mongo_url`        | `str`           | `"mongodb://localhost:27017/"` | The URL of the deployed MongoDB server.                                                                               |
| `storage_engine`   | `str`           | `"default"`                    | Specify in which server the collection is to be created. In a Milvus cluster, this refers to a server alias.             |
| `num_shards`       | `int`           | `1`                            | Specify the amount of nodes that one write operation in collection is distributed to, enhancing parallel computing.   |
| `embedding_type`   | `EmbeddingType` | `EmbeddingType.OpenAI_text_embedding_ada_002`      | The embedding algorithm used when embedding the description sentence into a vector.                                   |
| `metric_type`      | `MetricType`    | `MetricType.L2`                | The algorithm used to measure similarity among different vectors.                                                     |
| `idx_type`         | `IdxType`       | `IdxType.IVF_FLAT`             | The in-memory indexes supported by Milvus, which can be configured to achieve better search performance.              |
| `**idx_builder`    |                 |                                | Additional index builder parameters as a dictionary.                                                                  |

More about `idx_type` and `**idx_builder`: https://milvus.io/docs/v2.0.x/index.md


### 2 - Add batch of memories into basic memory object

```python
meta_data_dict_list = [{'importance': 10, 'area': 'london', 'mood': 'sad'},
                        {'importance': 8, 'area': 'nottinham', 'mood': 'extremely happy'},
                        {'importance': 2, 'area': 'birmingham', 'mood': 'peaceful'},
                        {'importance': 10, 'area': 'london', 'mood': 'fear'}]

description_list = ['Eric found that he was rejected by his dream graph',
                    'Eric started his first dating activity with a girl',
                    'Eric took the bus to catch system engineering lecture in University of Birmingham as usual',
                    'Eric found that his roommate, Stanley is a gay who want to do something to him']

full_contents_list = [{'content': 'Eric found that he was rejected by his dream graph'},
                      {'content': 'Eric started his first dating activity with a girl'},
                      {'content': 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'},
                      {'content': 'Eric found that his roommate, Stanley is a gay who want to do something to him'}]

save_time = ['2024-01-09 12:12:53', '2024-02-10 12:12:53', '2024-01-25 12:12:53', '2024-04-01 12:12:53']

# add the memory records into Milvus
result = bmm.add_memory(meta_data_dict_list, description_list, full_contents_list, save_time)

assert result == True
```


| Parameter               | Type              | Default | Description                                                                     |
|-------------------------|-------------------|---------|---------------------------------------------------------------------------------|
| `meta_data_dict_list`   | `List[Dict]`      |         | The list of customized filter metadata to be stored in Milvus.                  |
| `description_list`      | `List[str]`       |         | The list of description sentences to be stored in Milvus.                       |
| `full_content_dict_list`| `List[str]`       |         | The list of full content data to be stored in Milvus.                           |
| `save_time_list`        | `List[str]`       |         | The list of timestamps to be used in the new record.                            |

**Returns:** `bool` - Indicating whether the records are inserted into Milvus successfully.


### 3 - Query up to #limit amount of records that are similar to given query, supporting the filtering using meta_data_dict conditions

```python
query = ['who is Stanley, and what is the relationship between Stanley and Eric?']
current_access_time = '2024-07-14 09:02:53'

# query the memory records
result = bmm.search_memory(query, current_access_time)[0]

doc_id = result['docstore_id']   
meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']

assert meta_dict['importance'] == 10
assert meta_dict['area'] == 'london'
assert meta_dict['mood'] == 'fear'

assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'
```

| Parameter            | Type                  | Default | Description                                                                                   |
|----------------------|-----------------------|---------|-----------------------------------------------------------------------------------------------|
| `query`              | `List[str]`           |         | The list of queries being used to search from Milvus.                                         |
| `current_access_time`| `str`                 |         | The current timestamp when searching the query.                                               |
| `limit`              | `int`                 | `1000`  | The maximum amount of records to return.                                                      |
| `replica_num`        | `int`                 | `1`     | Specify how many query nodes the data will be loaded onto.                                    |
| `doc_id_list`        | `Optional[List[int]]` | `None`  | Optional. The list of specified doc_id, whose attached records are what we want to search from Milvus. |
| `meta_data_filter`   | `Optional[Dict]`      | `None`  | Optional. The dict to specify the keys in meta_data_dict to be used and their related filtering descriptions. |

**Returns:** `List[Dict]` - The memory records that are fetched from Milvus according to the query, including three fields: `docstore_id`, `meta_data_dict`, `full_content`.

### 4 - Filter up to #limit amount of records according to the given conditions

```python
filter_dict = {'importance': "== 2", 'mood': "in ['peaceful']"}
current_access_time = '2024-09-14 12:12:53'

# filter the memory records from Milvus according to specified metadata conditions
result = bmm.filter_memory(current_access_time, meta_data_filter=filter_dict)[0]

doc_id = result['docstore_id']   
meta_dict, full_content_dict = result['meta_data_dict'], result['full_content']

assert meta_dict['importance'] == 2
assert meta_dict['area'] == 'birmingham'
assert meta_dict['mood'] == 'peaceful'

assert full_content_dict['content'] == 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'

```

| Parameter            | Type                  | Default | Description                                                                                   |
|----------------------|-----------------------|---------|-----------------------------------------------------------------------------------------------|
| `current_access_time`| `str`                 |         | The current timestamp when executing the filter query.                                        |
| `limit`              | `int`                 | `1000`  | The maximum number of records to return.                                                      |
| `replica_num`        | `int`                 | `1`     | Specifies how many query nodes the data will be loaded onto.                                  |
| `doc_id_list`        | `Optional[List[int]]` | `None`  | Optional. The list of specified doc_id, whose attached records are targeted for filtering.    |
| `meta_data_filter`   | `Optional[Dict]`      | `None`  | Optional. Specifies the keys in meta_data_dict for use in filtering and their related descriptions. |

**Returns:** `List[Dict]` - The memory records fetched from Milvus according to the specified filtering conditions, including three fields: `docstore_id`, `meta_data_dict`, `full_content`.


### 5 - Delete the filtered records from Milvus

```python
filter_dict = {'importance': "== 2", 'mood': "in ['peaceful']"}

# delete the memory records that match this filter condition
result = bmm.delete_memory(meta_data_filter=filter_dict)

assert result == 1
```


| Parameter           | Type                | Default | Description                                                                                   |
|---------------------|---------------------|---------|-----------------------------------------------------------------------------------------------|
| `doc_id_list`       | `Optional[List[int]]` | `None`  | Optional. The list of specified doc_id, whose attached records are targeted for deletion.     |
| `replica_num`       | `int`               | `1`     | Specifies how many query nodes the data will be loaded onto for the operation.               |
| `meta_data_filter`  | `Optional[Dict]`    | `None`  | Optional. Specifies the keys in meta_data_dict for use in filtering records to be deleted.    |

**Returns:** `int` - Indicates how many records are successfully deleted from Milvus.


### 6 - Manage the attribute storage object, which is related to this BasicMemoryMechanism

```python
# insert or update one attribute record
result = bmm.update_attributes(
        collection_name = "test_collection", 
        attribute_type = "Mana", 
        key = "Character_1", 
        value = "Value_1"
    )
    
assert 'registered_attributes' in collection_bmm._mongo_db.list_collection_names()
assert 'Manaintest_collection' in collection_bmm._mongo_db['registered_attributes'].find()[0]['attributes']
assert result == True
```

```python
# retreieve one attribute record
result = bmm.get_attribute(
        collection_name = "test_collection", 
        attribute_type = "Mana", 
        key = "Character_1",
    )
    
assert result == 'Value_1'
```

```python
# delete one attribute record
result = collection_bmm.delete_attribute(
        collection_name = "test_collection", 
        attribute_type = "Mana", 
    )

assert 'Manaintest_collection' not in collection_bmm._mongo_db['registered_attributes'].find()[0]['attributes']

assert result == True
```
