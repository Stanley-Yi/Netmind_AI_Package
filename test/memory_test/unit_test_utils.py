import pytest
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

import random
import datetime

from xyz.magics.memory._embedding_setting.IdxTypeEnum import IdxType
from xyz.magics.memory._embedding_setting.MetricTypeEnum import MetricType
from xyz.magics.memory import utils 


start_date = datetime.date(2018, 1, 1)
end_date = datetime.date(2024, 12, 31)

def random_date():
    """Generate a random date between `start_date` and `end_date`"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date


# 测试配置
db_name = 'test_milvus_db'
coll_name = 'test_milvus_coll'
milvus_host = '18.171.129.243'
milvus_port = 80
milvus_user = "root"
milvus_psw = "NetMindMilvusDB"


# 建立 Milvus 连接的 Fixture
@pytest.fixture(scope='module')
def milvus_collection():
    connections.connect(host=milvus_host, port=milvus_port, user=milvus_user, password=milvus_psw)
    
    create_time = FieldSchema(
        name="create_time",
        dtype=DataType.VARCHAR,
        max_length=50,
    )

    last_modified = FieldSchema(
        name="last_modified",
        dtype=DataType.VARCHAR,
        max_length=50,
    )

    memory_id = FieldSchema(
        name="id",
        dtype=DataType.INT64,
        is_primary=True,
    )

    character_id = FieldSchema(
        name="character_id",
        dtype=DataType.INT64
    )

    importance = FieldSchema(
        name="importance",
        dtype=DataType.INT8,
    )

    category = FieldSchema(
        name="category",
        dtype=DataType.VARCHAR,
        max_length=50,
    )

    vector = FieldSchema(
        name="memory_vector",
        dtype=DataType.FLOAT_VECTOR,  # BINARY_VECTOR or FLOAT_VECTOR
        default_value=[1.0] * 1024,
        dim=1024
    )

    content = FieldSchema(
        name="real_memory",
        dtype=DataType.VARCHAR,
        max_length=9999,
        default_value="Unknown"
    )
    
    coll_schema = CollectionSchema(
        fields=[memory_id, character_id, importance, create_time, category, vector, content, last_modified],
        description="memory",
        
        # 不开启 dynamic 意味着之后插入的所有数据实体都要与 schema 匹配；而开启后，可以插入具有新字段的实体，有点类似 nonsql
        # https://milvus.io/docs/dynamic_schema.md#Create-collection-with-dynamic-schema-enabled
        enable_dynamic_field=True
    )

    collection_name = "character_memory"

    collection = Collection(
        name=collection_name,
        schema=coll_schema,
        using='default',  # 在哪个 server 上创建 collection
        shards_num=1,  # 把写入操作分配到 2 个不同的 node / server 上并行进行
        
    )
    
    entities = [
        [i for i in range(3000)],
        [i for i in range(3000)],
        [random.choice([1, 2]) for i in range(3000)],
        [random_date().strftime('%Y-%m-%d') for _ in range(3000)],
        ["observation" for _ in range(3000)],
        [[random.randint(0, 10)] * 1024 for _ in range(3000)],
        ["The test content" for _ in range(3000)],
        [random_date().strftime('%Y-%m-%d') for _ in range(3000)],
    ]
    
    collection = Collection("character_memory")      # Get an existing collection.
    collection.create_partition("observation")

    collection.insert(entities, 'observation') 
    # After final entity is inserted, it is best to call flush to have no growing segments left in memory
    collection.flush()
    
    return collection



# 正常创建 idx
def test_create_collection(milvus_collection):
    idx = utils.attach_idx(milvus_collection, "memory_vector", MetricType.L2, False, IdxType.IVF_FLAT, nlist=5)
    assert idx == {'metric_type': 'L2', 'index_type': 'IVF_FLAT', 'params': {'nlist': 5}}

    # 如果已经创建过 idx，则不再创建，返回之前的
    idx = utils.attach_idx(milvus_collection, "memory_vector", MetricType.IP, False, IdxType.IVF_FLAT, nlist=5)
    assert idx == {'metric_type': 'L2', 'index_type': 'IVF_FLAT', 'params': {'nlist': 5}}
    
    milvus_collection.drop_index()



# 正常创建 idx
def test_param_error(milvus_collection):
    
    # float vector 但 isBinary = True
    with pytest.raises(Exception):
        idx_builder = {'nlist': 5}
        utils.attach_idx(milvus_collection, "memory_vector", MetricType.L2, True, IdxType.IVF_FLAT, idx_builder=idx_builder)
    

    # idx_builder 参数错误
    with pytest.raises(Exception):
        idx_builder = {'nlist': 5, 'nbits': 3}
        utils.attach_idx(milvus_collection, "memory_vector", MetricType.L2, False, IdxType.IVF_SQ8, idx_builder=idx_builder)
    


# 清理测试数据   不要在此测试后添加测试！！！！
def test_cleanup(milvus_collection):
    
    for partition in milvus_collection.partitions:
        if partition.name != "_default":  # 不删除默认 partition
            milvus_collection.drop_partition(partition_name=partition.name)

    # 删除整个 collection
    milvus_collection.drop()