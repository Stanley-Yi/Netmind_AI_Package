

from pymilvus import connections, db, Collection, utility, CollectionSchema, FieldSchema, DataType
import pymysql
from user_settings import client
from typing import Dict, List, Optional



def create_collection(col_name: str):
    
    if col_name in utility.list_collections():
        return

    id = FieldSchema(
        name="id",
        dtype=DataType.INT64,
        is_primary=True,
        auto_id=True
    )

    sql_id = FieldSchema(
        name="sql_id",
        dtype=DataType.INT64
    )

    vector = FieldSchema(
        name="vector",
        dtype=DataType.FLOAT_VECTOR,
        dim=1536
    )

    category = FieldSchema(
        name="category",
        dtype=DataType.VARCHAR,
        max_length=10,
    )

    col_schema = CollectionSchema(
        fields=[id, sql_id, category, vector],
        description=col_name,
    )

    Collection(
        name=col_name,
        schema=col_schema,
        using='default',  # 在哪个 server 上创建 collection
        shards_num=1,  # 把写入操作分配到 2 个不同的 node / server 上并行进行
    )


def create_long_term_table(connection: pymysql.connections):
    cursor = connection.cursor()
    cursor.execute(f"SHOW TABLES LIKE 'long_term';")
    result = cursor.fetchone()
    if not result:
        create_table_sql = f"""
        CREATE TABLE long_term (
            id INT AUTO_INCREMENT PRIMARY KEY,
            parent_id INT NOT NULL,
            cur_level INT NOT NULL,
            cur_status TEXT NOT NULL,
            cur_goal TEXT, 
            action TEXT, 
            feedback TEXT,
            store_datetime DATETIME NOT NULL,
            final_status VARCHAR(30)
        );
        """
        cursor.execute(create_table_sql)
    
    # cursor.execute("ALTER TABLE long_term ADD CONSTRAINT fk_root_id FOREIGN KEY (root_id) REFERENCES long_term(id);")
    # cursor.execute("ALTER TABLE long_term ADD CONSTRAINT fk_leaf_id FOREIGN KEY (leaf_id) REFERENCES long_term(id);")    
    # connection.commit()
    cursor.close()



def create_short_term_table(connection: pymysql.connections):
    cursor = connection.cursor()
    cursor.execute(f"SHOW TABLES LIKE 'short_term';")
    result = cursor.fetchone()
    if not result:
        create_table_sql = f"""
        CREATE TABLE short_term (
            id INT AUTO_INCREMENT PRIMARY KEY,
            parent_id INT NOT NULL,
            cur_level INT NOT NULL,
            cur_status TEXT NOT NULL,
            cur_goal TEXT, 
            action TEXT, 
            feedback TEXT,
            store_datetime DATETIME NOT NULL,
            final_status VARCHAR(30)
        );
        """
        cursor.execute(create_table_sql)
    # cursor.execute("ALTER TABLE short_term ADD CONSTRAINT fk_parent_id FOREIGN KEY (parent_id) REFERENCES short_term(id);")
    # connection.commit()    
    cursor.close()



def embedding_content(content: List[str],) -> List[List[float]]:
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

    if not content:
        return []
            
    embedding_res = []

    try:
        for i in content:
            
            respond = client.embeddings.create(
                model='text-embedding-ada-002',   # 之后可以加一个配置文件，配置这些内容
                input=i,
                encoding_format="float"
            )
            embedding_res.append(respond.data[0].embedding)

    except Exception as err:
        raise err

    return embedding_res
