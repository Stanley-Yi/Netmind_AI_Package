"""
====================
MomentumMemory
====================
@file_name: MomentumMemory.py
@author: Tianlei Shi, BlackSheep-Team, Netmind.AI
@date: 2024-2-7
The basic memory object, which has all function needed for momentum module
"""


from pymilvus import connections, db, Collection, utility, CollectionSchema, FieldSchema, DataType
from typing import Dict, List, Optional
import pymysql
import utils
from datetime import datetime
from anytree import Node, RenderTree



class MomentumMemory:
    '''
        设计思路：
        milvus 只储存 embedding 后的 vector, 以及 id (对应数据库中的哪一条), 还有一个值来表明它是 currect status, goal, feedback 还是 action
        milvus 里使用 “long_term” 和 “short_term” 两个 collection 来储存不同的 memory
        
        
        sql 里储存其他所有的必须信息，包括：
            long_term:
                root 节点 (goal 的描述), goal status 节点, 当前的步数（这样设计可以最快查询出一条完整路径) x
                上一步的 id, 当前的步数
                currect status, goal, 和 action, feedback 的文字（不储存在 milvus 里是为了利用 sql 的高性能）
                id (关联 embedding vector)
                储存时间
                最终结果 (success, fail, uncompleted)
            
            short_term:
                上一步的 id, 当前的步数 (可能尝试不同的分支, 因此数据以树状结构存在, 所以需要知道父节点 - 即上一步; 该部分在储存到 long_term 时需要转换 x)
                currect status, goal, 和 action, feedback 的文字
                id (关联 embedding vector)
                储存时间
                最终结果 (empty - 未走完的路径, success, fail; 没得到最后结果前, 所有都是 empty, 得到最终结果后, 在储存到 long_term 的时候再处理每个路径上的值)
            
        回溯方面的想法：
            把数据库当成一个栈, 如果当前步骤失败了, 就把上一步弹出来, 看能不能找其他路
            
        遗忘机制
    '''

    def __init__(self,
                 milvus_db: str = 'momentum_milvus_db',
                 sql_db: str = 'momentum_sql_db',
                 milvus_host: str = 'localhost',
                 milvus_port: int = 19530,
                 milvus_user: str = 'root',
                 milvus_psw: str = 'milvus',
                 sql_host: str = 'localhost',
                 sql_port: int = 3306,
                 sql_user: str = 'root',
                 sql_psw: str = '',
                 milvus_index: str = 'IVF_FLAT') -> None:
        
        """Initialize the MomentumMemory module, 
        
        1. connect to milvus and mysql database
        2. use or create specified database
        3. create long-term and short-term tables or collections

        Parameters
        ----------
        milvus_db : str = 
            database name of milvus, by default 'momentum_milvus_db',
        sql_term_db: str = 'momentum_sql_db',
        milvus_host: str = 'localhost',
        milvus_port: int = 19530,
        milvus_user: str = 'root',
        milvus_psw: str = 'milvus',
        sql_host: str = 'localhost',
        sql_port: int = 3306,
        sql_user: str = 'root',
        sql_psw: str = '',
        milvus_index: str = 'IVF_FLAT'

        Returns
        -------
        list
            _description_
        """
        
        # config of milvus and mysql database
        self.milvus_db = {"host": milvus_host, "port": milvus_port, "user": milvus_user, "password": milvus_psw, "database": milvus_db}
        self.sql_db = {"host": sql_host, "port": sql_port, "user": sql_user, "password": sql_psw, "database": sql_db}
        
        self.index_type = milvus_index

        try:
            # interface milvus db
            connections.connect(host=milvus_host, port=milvus_port, user=milvus_user, password=milvus_psw)
            if milvus_db not in db.list_database():
                db.create_database(milvus_db)
            db.using_database(milvus_db)
            
            # create collection
            utils.create_collection('long_term')
            utils.create_collection('short_term')
        except Exception as e:
            raise e
            
        try:
            # interface mysql db
            sql_con = pymysql.connect(host=sql_host, port=sql_port, user=sql_user, password=sql_psw,)
            
            with sql_con.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {sql_db}")
        finally:
            sql_con.close()
        
        try:
            self._sql_con = pymysql.connect(host=sql_host, port=sql_port, user=sql_user, password=sql_psw, database=sql_db,)
            
            utils.create_long_term_table(self._sql_con)
            utils.create_short_term_table(self._sql_con)
        except Exception as e:
            raise e
    
    
    def __del__(self) -> None:
        """Destructor of the MomentumMemory module
        
            Close mysql connection
        """
        
        self._sql_con.close()
        
    
        
    def save_memory(self,
                    last_step: int,
                    cur_level: int,
                    status: str,
                    goal: str,
                    action: str,
                    feedback: str,
                    fianl_status: str = 'uncompleted') -> int:
        """Add memory of current step to short-term memory
        Parameters
        ----------
        last_step : int
            id of the previous step stored in the database. -1 if this is the first step
        cur_level : int
            current level (or step number) in the whole task
        status : str
            description of current status
        goal : str
            description of current goal
        action : str
            description of the action base on status and goal
        feedback : str
            description of feedback for the action

        Returns
        -------
        int
            id of this step stored in the database
        """
        
        content = [status, goal, action, feedback]
        embeddings = utils.embedding_content(content)
        
        try:
            with self._sql_con.cursor() as cursor:
                insert_sql = """
                INSERT INTO short_term (parent_id, cur_level, cur_status, cur_goal, action, feedback, store_datetime, final_status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                store_time = datetime.now()
                data = (last_step, cur_level, status, goal, action, feedback, store_time, fianl_status)
                
                cursor.execute(insert_sql, data)
                insert_id = cursor.lastrowid
                self._sql_con.commit()
        except Exception as e:
            raise e
        
        try:
            entities = [
                [insert_id] * 4,
                ['status', 'goal', 'action', 'feedback'],
                embeddings
            ]
            collection = Collection("short_term")  
            collection.insert(entities)
        except Exception as e:
            raise e
        
        return insert_id
    
    
    
    def update_memory():
        """对 short-term memory 里的记录进行更新，根据 id 更新
        """
        pass
    
    
    def update_final_status(self, start_id, final_status, limit = 100000):
        """从底下往上开始更新状态（因为知道父节点）。
            对 short-term memory 进行操作，start_id 是开始的 id；limit 是更新几个，如果不指定的话，就一直更新到 root
            建议出现 fail 或 success 就要调用一次
        """
        allowed_statuses = ["success", "fail", "uncompleted"]
    
        if final_status not in allowed_statuses:
            raise ValueError(f"Invalid final_status: {final_status}. Allowed values are: {allowed_statuses}")
        if not limit >= 1:
            raise ValueError(f"Invalid limit: {limit}. Limit value should larger or equals to 1")
        
        try:
            with self._sql_con.cursor() as cursor:                
                select_sql = f"""
                WITH RECURSIVE LevelChain AS (
                    SELECT *, 1 AS Depth FROM short_term WHERE id = {start_id}
                    UNION ALL
                    SELECT t.*, lc.Depth + 1 FROM short_term t
                    INNER JOIN LevelChain lc ON t.id = lc.parent_id
                    WHERE lc.Depth < {limit}
                )
                SELECT LevelChain.id FROM LevelChain ORDER BY LevelChain.cur_level;                 
                """
                cursor.execute(select_sql)
                target_ids = [row[0] for row in cursor.fetchall()]
                
                for id in target_ids:
                    update_sql = f"UPDATE short_term SET final_status = '{final_status}' WHERE id = {id}"
                    cursor.execute(update_sql)
                self._sql_con.commit()
                
        except Exception as e:
            raise e

    
    def get_memory_by_ID():
        pass
    
    
    def get_child_id(self,  cur_id: int, table: str):
        """treat pass id as root id, find its all child id
        """
        with self._sql_con.cursor() as cursor:
            child_sql = f"SELECT t.id FROM (SELECT id, parent_id FROM {table} WHERE parent_id = {cur_id}) t;"
            cursor.execute(child_sql)
            child_res = cursor.fetchall()

        if child_res:
            return [x[0] for x in child_res]
    
    
    def _get_all_child_id(self, root_id: int, table: str):
        """treat pass id as root id, find its all child id
        """
        with self._sql_con.cursor() as cursor:
            tree_sql = f"WITH RECURSIVE TreeCTE AS ( SELECT id, parent_id FROM {table} WHERE id = {root_id} UNION ALL SELECT yt.id, yt.parent_id FROM {table} yt JOIN TreeCTE cte ON yt.parent_id = cte.id ) SELECT id FROM TreeCTE;"
            cursor.execute(tree_sql)
            tree_res = cursor.fetchall()

        if tree_res:
            return [x[0] for x in tree_res]
        
    
    def _get_whole_tree_id(self, cur_id: int, table: str = 'short_term'):
        root_id = self.get_root_id(cur_id, table)

        # find all tree id
        if root_id != -1:
            return self._get_all_child_id(root_id, table)
    
    
    def _get_single_path(self, cur_id: int, table: str = 'short_term'):
        """
        """
        nodes_data = []
        
        with self._sql_con.cursor() as cursor:
            root_cur_sql = f"""
                WITH RECURSIVE LevelChain AS (
                    SELECT * FROM {table} WHERE id = {cur_id}
                    UNION ALL
                    SELECT t.* FROM {table} t
                    INNER JOIN LevelChain lc ON t.id = lc.parent_id
                )
                SELECT LevelChain.* FROM LevelChain ORDER BY LevelChain.cur_level;                 
                """
            cursor.execute(root_cur_sql)
            root_cur = cursor.fetchall()
            if len(root_cur) > 0:
                nodes_data += [{"id": row[0], "parent_id": row[1], "cur_status": row[3], "action": row[5], "cur_level": row[2]} for row in root_cur[:-1]]
            
            child_sql = f"WITH RECURSIVE TreeCTE AS ( SELECT * FROM {table} WHERE id = {cur_id} UNION ALL SELECT yt.* FROM {table} yt JOIN TreeCTE cte ON yt.parent_id = cte.id ) SELECT * FROM TreeCTE;"
            cursor.execute(child_sql)
            child_res = cursor.fetchall()
            if len(child_res) > 0:
                nodes_data += [{"id": row[0], "parent_id": row[1], "cur_status": row[3], "action": row[5], "cur_level": row[2]} for row in child_res]
        
        return nodes_data
            
    
    def show_memory(self, id: int, is_tree: bool = True, table: str = 'short_term') -> None:
        """根据 id, 打印 id 所属的整个 tree, 或整条 action chain
        """
        all_id = self._get_whole_tree_id(id, table)
        
        nodes_data = []
        
        if is_tree:
            with self._sql_con.cursor() as cursor:
                select_sql = f"SELECT id, parent_id, cur_status, action, cur_level FROM {table} WHERE id IN ({', '.join(str(id) for id in all_id)})"
                cursor.execute(select_sql)

                result = cursor.fetchall()

                nodes_data = [{"id": row[0], "parent_id": row[1], "cur_status": row[2], "action": row[3], "cur_level": row[4]} for row in result]
        else:
            nodes_data = self._get_single_path(id, table)
        
        self._print_memory_tree(nodes_data)

    
    def _print_memory_tree(self, data) -> None:
        nodes = {}
        root_id = -1

        for node_data in data:
            nodes[node_data["id"]] = Node(str(node_data["id"]) + ': ' + node_data["cur_status"] + '\n' + ('     ' * node_data["cur_level"]) + node_data["action"])
            if node_data["parent_id"] == -1:
                root_id = node_data["id"]

        for node_data in data:
            node = nodes[node_data["id"]]
            parent_id = node_data["parent_id"]
            if parent_id != -1:
                node.parent = nodes[parent_id]
        
        print('\n')
        for pre, fill, node in RenderTree(nodes[root_id]):
            print("%s%s" % (pre, node.name))
    

    def check_create_index(self, collection_name):
        collect = Collection(collection_name)
        
        if collect.has_index():
            return
        else:
            index = {"index_type": "IVF_FLAT", "params": {"nlist": 4}, "metric_type": "L2"}
            collect.create_index("vector", index)


    def get_root_id(self, cur_id: int, table: str):
        with self._sql_con.cursor() as cursor:
            root_sql = f"WITH RECURSIVE CTE AS (SELECT * FROM {table} WHERE id = {cur_id} UNION ALL SELECT t.* FROM {table} t JOIN CTE c ON t.id = c.parent_id) SELECT id FROM CTE where parent_id = -1;"
            cursor.execute(root_sql)
            root_res = cursor.fetchall()

            if root_res:
                root_id = root_res[0][0]
                return root_id
    

    def end_task(self, end_id: int):
        '''
            store short term memory to long term memory
        '''
        # find root id
        root_id = -1
        leaf_ids = dict()
        
        try:
            with self._sql_con.cursor() as cursor:
                # find root id
                root_id = self.get_root_id(end_id, 'short_term')
                
                # find all leaf id
                if root_id != -1:
                    leaf_sql = f"WITH RECURSIVE SubTree AS ( SELECT * FROM short_term WHERE parent_id = {root_id} UNION ALL SELECT yt.* FROM short_term yt INNER JOIN SubTree st ON yt.parent_id = st.id ) SELECT id, cur_level, final_status FROM SubTree WHERE id NOT IN (SELECT parent_id FROM short_term WHERE parent_id != -1);"
                    cursor.execute(leaf_sql)
                    leaf_res = cursor.fetchall()

                    if leaf_res:
                        for x in leaf_res:
                            if x[2] in leaf_ids:  # 根据 final_status 进行录入, 路径越短的越先录
                                max_stack = leaf_ids[x[2]]  # 路径越长, 越往后排
                                added = False
                                for i in range(len(max_stack)):
                                    if x[1] < max_stack[i][1]:
                                        max_stack.insert(i, (x[0], x[1]))
                                        added = True
                                if not added:
                                    max_stack.append((x[0], x[1]))
                            else:
                                leaf_ids[x[2]] = [(x[0], x[1])]  # id, level - 路径长度
                
                # transfer memory from short_term to long_term
                record_nodes = set()
                short_long_id = dict()  # 进行 id 的映射 {short_id : long_id}
                
                self.check_create_index('short_term')
                short_term = Collection('short_term')
                long_term = Collection('long_term')
                short_term.load()
                
                for s in ["success", "fail", "uncompleted"]:
                    if s not in leaf_ids:
                        continue
                    
                    for i in leaf_ids[s]:
                        path_sql = f"""
                            WITH RECURSIVE LevelChain AS (
                                SELECT * FROM short_term WHERE id = {i[0]}
                                UNION ALL
                                SELECT t.* FROM short_term t
                                INNER JOIN LevelChain lc ON t.id = lc.parent_id
                            )
                            SELECT LevelChain.* FROM LevelChain ORDER BY LevelChain.cur_level;                 
                        """
                        cursor.execute(path_sql)
                        cur_path = [row for row in cursor.fetchall()]  # 获取一条 action chain
                        
                        for record in cur_path:
                            if record[0] in record_nodes:  # 如果已经储存在 long_term 里了
                                continue
                            
                            last_tree_num_sql = "SELECT tree_num FROM long_term ORDER BY tree_num DESC LIMIT 1"
                            cursor.execute(last_tree_num_sql)
                            last_tree_num = cursor.fetchone()
                            tree_num = 1
                            if last_tree_num:
                                tree_num = last_tree_num[0]
                            
                            insert_sql = """
                                INSERT INTO long_term (tree_num, parent_id, cur_level, cur_status, cur_goal, action, feedback, store_datetime, final_status) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            
                            data = (tree_num, short_long_id[record[1]] if record[1] in short_long_id else -1, record[2], record[3], record[4], record[5], record[6], record[7], record[8])
                            cursor.execute(insert_sql, data)
                            insert_id = cursor.lastrowid
                            self._sql_con.commit()
                            
                            record_nodes.add(record[0])
                            short_long_id[record[0]] = insert_id

                            # handle milvus
                            res = short_term.query(
                                expr = f"sql_id == {record[0]}",
                                output_fields = ['vector', 'category'],
                            )
                            
                            vector_item, category_item = [], []
                            
                            for m in res:
                                vector_item.append(m["vector"])
                                category_item.append(m["category"])
                            
                            entities = [
                                [insert_id] * len(res),
                                category_item,
                                vector_item
                            ]
                            
                            long_term.insert(entities)
                            short_term.delete(f"sql_id == {record[0]}")

                # delete transfered short_term data
                delete_ids = ', '.join(str(id) for id in record_nodes)
                delete_sql = f"DELETE FROM short_term WHERE id IN ({delete_ids})"
                cursor.execute(delete_sql)
                self._sql_con.commit()
                
                short_term.flush()

        except Exception as e:
            raise e
        
    

    def search_memory(self, status: str, goal: str, is_shortest: bool = True):
        self.check_create_index('long_term')
        long_term = Collection('long_term')
        long_term.load()
        
        status_set, goal_set = set(), set()
        
        em_status, em_goal = utils.embedding_content([status, goal])
        
        search_params = {
            "metric_type": "L2", 
            "offset": 0, 
            "ignore_growing": False, 
            "params": {"nprobe": 2}
        }
        
        status_res = long_term.search(
            data=[em_status], 
            anns_field="vector", 
            param=search_params,
            limit=5,
            expr="category == 'status'",
            output_fields=['sql_id']
        )
        for hit in status_res[0]:
            sql_id = hit.entity.get('sql_id') if hasattr(hit, 'entity') and callable(hit.entity.get) else None
            if sql_id is not None:
                status_set.add(sql_id)
        
        goal_res = long_term.search(
            data=[em_goal], 
            anns_field="vector", 
            param=search_params,
            limit=5,
            expr="category == 'goal'",
            output_fields=['sql_id']
        )
        for hit in goal_res[0]:
            sql_id = hit.entity.get('sql_id') if hasattr(hit, 'entity') and callable(hit.entity.get) else None
            if sql_id is not None:
                goal_set.add(sql_id)
        

        # get all record
        path_record = dict()
        with self._sql_con.cursor() as cursor:
            status_sql = f"SELECT * FROM long_term WHERE id IN ({', '.join(str(id) for id in status_set)}) AND final_status = 'success'"
            cursor.execute(status_sql)
            status_rec = cursor.fetchall()

            if status_rec:
                for x in status_rec:
                    if x[1] in path_record:
                        if path_record[x[1]]['status'][0][3] > x[3]:
                            path_record[x[1]]['status'] = [x]
                    else:
                        path_record[x[1]] = {'status': [x]}
            else:
                return []
            
            goal_sql = f"SELECT * FROM long_term WHERE id IN ({', '.join(str(id) for id in goal_set)}) AND final_status = 'success'"
            cursor.execute(goal_sql)
            goal_rec = cursor.fetchall()

            if status_rec:
                for x in goal_rec:
                    if x[1] in path_record:
                        if 'goal' in path_record[x[1]]:
                            path_record[x[1]]['goal'].append(x)
                        else:
                            path_record[x[1]]['goal'] = [x]
                    else:  # 如果没有 status，则不记录这棵 tree
                        continue
            else:
                return []
            
        # 没整完，等和 flow 和 energy + importance 结合
        return path_record
        # result = []
        # for k, v in path_record.items():
            
            
        # return result
    
    
    def search_status():
        pass
    
    
    def search_goal():
        pass
    
    
    def search_action():
        pass
    
    
    def find_shortest_path():
        pass
    
    
    def find_all_possible_path():
        pass
    