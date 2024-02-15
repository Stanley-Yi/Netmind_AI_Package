import pytest

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from MomentumMemory import MomentumMemory
from pymilvus import utility, Collection

"""
The unit test case for MomentumMemory class

"""

@pytest.fixture(scope='module')
def memory_instance() -> MomentumMemory:

    # initialize the collection-level memory storage unit
    return MomentumMemory(
            sql_db = 'momentum_sql_db',
            milvus_host = '18.171.129.243',
            milvus_port = 80,
            milvus_user = 'root',
            milvus_psw = 'NetMindMilvusDB',
            sql_host = '18.171.129.243',
            sql_port = 3306,
            sql_user = 'netmind',
            sql_psw = 'NetMindMySQL',
        )


def test_save_memory_1(memory_instance):
    # step 1 - success
    step_1_status = 'Exceeding weight by 10 kilograms.'
    step_1_goal = 'Reduce weight of 10 kg.'
    step_1_action = 'Establish a weight loss plan including diet and exercise.'
    step_1_feedback = 'Setting up a weight loss plan is the first step in starting the weight loss journey, laying the foundation for subsequent actions.'
    step_1 = memory_instance.save_memory(-1, 1, step_1_status, step_1_goal, step_1_action, step_1_feedback)
    
    # step 2 - success
    step_2_status = 'Weight loss plan established.'
    step_2_goal = 'Improve dietary habits to reduce weight.'
    step_2_action = 'Develop a healthy eating plan, reducing intake of high-calorie foods and increasing the proportion of vegetables and fruits.'
    step_2_feedback = 'Improving dietary habits helps control calorie intake, which is key to successful weight loss.'
    step_2 = memory_instance.save_memory(step_1, 2, step_2_status, step_2_goal, step_2_action, step_2_feedback)
    
    # step 3.1 - fail
    step_3P1_status = 'Improved eating habits have shown results, with a weight loss of 5 kg, but the target of 10 kg has not yet been reached'
    step_3P1_goal = 'Reduce the remaining 5kg through exercise.'
    step_3P1_action = 'Engage in outdoor activities such as brisk walking or cycling daily.'
    step_3P1_feedback = 'As an office worker, the frequency and intensity of outdoor exercise cannot meet the goal of losing 5 kg.'
    step_3P1 = memory_instance.save_memory(step_2, 3, step_3P1_status, step_3P1_goal, step_3P1_action, step_3P1_feedback)
    
    memory_instance.update_final_status(step_3P1, 'fail')
    
    # step 3.2 - success
    step_3P2_status = 'Improved eating habits have shown results, with a weight loss of 5 kg, but the target of 10 kg has not yet been reached'
    step_3P2_goal = 'Reduce the remaining 5kg through exercise.'
    step_3P2_action = 'Join a gym and engage in regular aerobic and strength training.'
    step_3P2_feedback = 'Gyms can provide high-frequency and high-intensity training, which is an effective option for weight loss.'
    step_3P2 = memory_instance.save_memory(step_2, 3, step_3P2_status, step_3P2_goal, step_3P2_action, step_3P2_feedback)
    
    # step 4.2.1 - fail
    step_4P2P1_status = 'Joined a gym and needs to choose a physical activity to lose 5 kg.'
    step_4P2P1_goal = 'Choose exercises suitable for rapid weight loss.'
    step_4P2P1_action = 'Participating in aerobic dance classes.'
    step_4P2P1_feedback = 'The weight loss speed of aerobic dance is too slow and prone to rebound.'
    step_4P2P1 = memory_instance.save_memory(step_3P2, 4, step_4P2P1_status, step_4P2P1_goal, step_4P2P1_action, step_4P2P1_feedback)
    
    memory_instance.update_final_status(step_4P2P1, 'fail')
    
    # step 4.2.2 - success
    step_4P2P2_status = 'Joined a gym and needs to choose a physical activity to lose 5 kg.'
    step_4P2P2_goal = 'Choose exercises suitable for rapid weight loss.'
    step_4P2P2_action = 'Engaged in HIIT training.'
    step_4P2P2_feedback = 'The training intensity of HIIT training is very high and it is specially designed for weight loss. It is very right to choose this exercise.'
    step_4P2P2 = memory_instance.save_memory(step_3P2, 4, step_4P2P2_status, step_4P2P2_goal, step_4P2P2_action, step_4P2P2_feedback)
    
    # step 5.2.2 - success
    step_5_status = 'Achieve weight loss goals through physical exercise'
    step_5_goal = ''
    step_5_action = ''
    step_5_feedback = 'By improving your dietary habits and choosing high-frequency and high-intensity running, you can effectively achieve your weight loss goals.'
    step_5 = memory_instance.save_memory(step_4P2P2, 5, step_5_status, step_5_goal, step_5_action, step_5_feedback)
    
    memory_instance.update_final_status(step_5, 'success')
    
    
    # test if data recorded into milvus and mysql
    with memory_instance._sql_con.cursor() as cursor:
        select_sql = "SELECT count(id) FROM short_term"
        cursor.execute(select_sql)
        result = cursor.fetchall()[0][0]
        assert result == 7
        
        select_sql = "SELECT count(id) FROM long_term"
        cursor.execute(select_sql)
        result = cursor.fetchall()[0][0]
        assert result == 0
    
    memory_instance.check_create_index('short_term')
    memory_instance.check_create_index('long_term')    
    short_term = Collection('short_term')
    short_term.load()
    long_term = Collection('long_term')
    long_term.load()
    
    res = long_term.query(
        expr = "",
        limit = 100,
        output_fields = ['category'],
    )
    assert len(res) == 0
    
    res = short_term.query(
        expr = "",
        limit = 100,
        output_fields = ['category'],
    )
    assert len(res) != 0
    
    memory_instance.end_task(step_5)
    
    # test if transfered
    with memory_instance._sql_con.cursor() as cursor:
        select_sql = "SELECT count(id) FROM short_term"
        cursor.execute(select_sql)
        result = cursor.fetchall()[0][0]
        assert result == 0
        
        select_sql = "SELECT count(id) FROM long_term"
        cursor.execute(select_sql)
        result = cursor.fetchall()[0][0]
        assert result == 7
    
    res = long_term.query(
        expr = "",
        limit = 100,
        output_fields = ['category'],
    )
    assert len(res) != 0
    
    res = short_term.query(
        expr = "",
        limit = 100,
        output_fields = ['category'],
    )
    assert len(res) == 0
    
    short_term.flush()
    long_term.flush()



# def test_save_memory_2(memory_instance):
#     # step 1 - success
#     step_1_status = 'Weighing more than 220 kg, seriously affecting the health.'
#     step_1_goal = 'Reduce weight to 150 kg.'
#     step_1_action = 'Losing weight through drugs and surgery.'
#     step_1_feedback = 'Determined to achieve rapid weight loss through surgery and medication to achieve good health.'
#     step_1 = memory_instance.save_memory(-1, 1, step_1_status, step_1_goal, step_1_action, step_1_feedback)
    
#     # step 2.1 - success
#     step_2_status = 'Weight loss plan established.'
#     step_2_goal = 'Improve dietary habits to reduce weight.'
#     step_2_action = 'Develop a healthy eating plan, reducing intake of high-calorie foods and increasing the proportion of vegetables and fruits.'
#     step_2_feedback = 'Improving dietary habits helps control calorie intake, which is key to successful weight loss.'
#     step_2 = memory_instance.save_memory(step_1, 2, step_2_status, step_2_goal, step_2_action, step_2_feedback)


# def test_clean_data(memory_instance):
#     try:
#         with memory_instance._sql_con.cursor() as cursor:
#             sql = f"TRUNCATE TABLE short_term;"
#             cursor.execute(sql)
            
#             sql = f"TRUNCATE TABLE long_term;"
#             cursor.execute(sql)
            
#             memory_instance._sql_con.commit()
            
#     except Exception as e:
#         print(f"Error: {e}")

    
#     try:
#         utility.drop_collection('short_term')
#         utility.drop_collection('long_term')
#     except Exception as e:
#         print(f"Error: {e}")



# def test_save_memory_collection(collection_bmm):
#     meta_data_dict_list = [{'importance': 10, 'area': 'london', 'mood': 'sad'},
#                         {'importance': 8, 'area': 'nottinham', 'mood': 'extremely happy'},
#                         {'importance': 2, 'area': 'birmingham', 'mood': 'peaceful'},
#                         {'importance': 10, 'area': 'london', 'mood': 'fear'}]

#     description_list = ['Eric found that he was rejected by his dream company',
#                     'Eric started his first dating activity with a girl',
#                     'Eric took the bus to catch system engineering lecture in University of Birmingham as usual',
#                     'Eric found that his roommate, Stanley is a gay who want to do something to him']

#     full_contents_list = [{'content': 'Eric found that he was rejected by his dream company'},
#                       {'content': 'Eric started his first dating activity with a girl'},
#                       {'content': 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'},
#                       {'content': 'Eric found that his roommate, Stanley is a gay who want to do something to him'}]

#     save_time = ['2024-01-09 12:12:53', '2024-02-10 12:12:53', '2024-01-25 12:12:53', '2024-04-01 12:12:53']

#     result = collection_bmm.save_memory(meta_data_dict_list, description_list, full_contents_list, save_time)
#     assert result == True


# def test_save_memory_partition(partition_bmm):
#     meta_data_dict_list = [{'importance': 10, 'area': 'london', 'mood': 'sad'},
#                         {'importance': 8, 'area': 'nottinham', 'mood': 'extremely happy'},
#                         {'importance': 2, 'area': 'birmingham', 'mood': 'peaceful'},
#                         {'importance': 10, 'area': 'london', 'mood': 'fear'}]

#     description_list = ['Eric found that he was rejected by his dream company',
#                     'Eric started his first dating activity with a girl',
#                     'Eric took the bus to catch system engineering lecture in University of Birmingham as usual',
#                     'Eric found that his roommate, Stanley is a gay who want to do something to him']

#     full_contents_list = [{'content': 'Eric found that he was rejected by his dream company'},
#                       {'content': 'Eric started his first dating activity with a girl'},
#                       {'content': 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'},
#                       {'content': 'Eric found that his roommate, Stanley is a gay who want to do something to him'}]

#     save_time = ['2024-01-09 12:12:53', '2024-02-10 12:12:53', '2024-01-25 12:12:53', '2024-04-01 12:12:53']

#     result = partition_bmm.save_memory(meta_data_dict_list, description_list, full_contents_list, save_time)
#     assert result == True


# def test_search_memory_collection(collection_bmm):
#     query = ['who is Stanley, and what is the relationship between Stanley and Eric?']
#     current_access_time = '2024-07-14 09:02:53'
#     result = collection_bmm.search_memory(query, current_access_time)[0]
    
#     meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
#     assert meta_dict['importance'] == 10
#     assert meta_dict['area'] == 'london'
#     assert meta_dict['mood'] == 'fear'

#     assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'


# def test_search_memory_partition(partition_bmm):
#     query = ['who is Stanley, and what is the relationship between Stanley and Eric?']
#     current_access_time = '2024-07-14 09:02:53'
#     result = partition_bmm.search_memory(query, current_access_time)[0]
    
#     meta_dict, full_content_dict = result['meta_data_dict'], result['full_content_dict']
    
#     assert meta_dict['importance'] == 10
#     assert meta_dict['area'] == 'london'
#     assert meta_dict['mood'] == 'fear'

#     assert full_content_dict['content'] == 'Eric found that his roommate, Stanley is a gay who want to do something to him'


# def test_filter_memory_collection(collection_bmm):
#     filter = {'importance': "== 2", 'mood': "in ['peaceful']"}
#     current_access_time = '2024-09-14 12:12:53'
#     result = collection_bmm.filter_memory(current_access_time, meta_data_filter=filter)[0]

#     meta_dict, full_content_dict = result['meta_data_dict'], result['full_content']
    
#     assert meta_dict['importance'] == 2
#     assert meta_dict['area'] == 'birmingham'
#     assert meta_dict['mood'] == 'peaceful'

#     assert full_content_dict['content'] == 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'


# def test_filter_memory_partition(partition_bmm):
#     filter = {'importance': "== 2", 'mood': "in ['peaceful']"}
#     current_access_time = '2024-09-01 12:12:53'
#     result = partition_bmm.filter_memory(current_access_time, meta_data_filter=filter)[0]

#     meta_dict, full_content_dict = result['meta_data_dict'], result['full_content']
    
#     assert meta_dict['importance'] == 2
#     assert meta_dict['area'] == 'birmingham'
#     assert meta_dict['mood'] == 'peaceful'

#     assert full_content_dict['content'] == 'Eric took the bus to catch system engineering lecture in University of Birmingham as usual'


# def test_delete_memory_collection(collection_bmm):
#     filter = {'importance': "== 2", 'mood': "in ['peaceful']"}
#     result = collection_bmm.delete_memory(meta_data_filter=filter)
    
#     assert result == 1


# def test_delete_memory_partition(partition_bmm):
#     filter = {'importance': "== 2", 'mood': "in ['peaceful']"}
#     result = partition_bmm.delete_memory(meta_data_filter=filter)
    
#     assert result == 1