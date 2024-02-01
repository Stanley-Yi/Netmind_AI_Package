import time
import random
from datetime import datetime
from pymilvus import utility


float_metric_type = ['L2', 'IP', 'COSINE']
binary_metric_type = ['JACCARD', 'HAMMING']

float_idx_type = ['FLAT', 'IVF_FLAT', 'IVF_SQ8', 'IVF_PQ', 'GPU_IVF_FLAT*', 'GPU_IVF_PQ*>', 'HNSW', 'DISKANN*']
binary_idx_type = ['BIN_FLAT', 'BIN_IVF_FLAT']

flat_param = []

def attach_idx(collection, field_name, metric_type, isBinary, idx_type, **idx_builder):

    # check metric and index type
    if isBinary:
        if metric_type.name not in binary_metric_type:
            raise Exception("The available metric type of binary index are: {}".format(', '.join(binary_metric_type)))
        if idx_type.name not in binary_idx_type:
            raise Exception("The available index type of binary index are: {}".format(', '.join(binary_idx_type)))
    else:
        if metric_type.name not in float_metric_type:
            raise Exception("The available metric type of float index are: {}".format(', '.join(float_metric_type)))
        if idx_type.name not in float_idx_type:
            raise Exception("The available index type of float index are: {}".format(', '.join(float_idx_type)))
    
    # check index builder and params
    try:
        index = collection.indexes

        if len(index) > 0:
            return index[0].params

        index_params = {
            "metric_type":metric_type,
            "index_type":idx_type,
            "params": idx_builder['idx_builder'] if idx_builder['idx_builder'] else {'nlist': 5}
        }
  
        collection.create_index(
            field_name=field_name, 
            index_params=index_params
        )

        print(utility.index_building_progress(collection.name))
        
    except Exception as err:
        raise err
    
    return collection.index().params

    

def generate_int64_id():
    # Use the current time to get the first 32 bits
    timestamp = int(time.time())
    # Generate a random number for the last 32 bits
    random_bits = random.getrandbits(32)
    # Combine them to get a 64-bit integer
    int64_id = (timestamp << 32) | random_bits
    return int64_id


def is_valid_timestamp(timestamp_str):
    try:
        # Attempt to convert the string to datetime object
        # Specify the expected format 'YYYY-MM-DD HH:MM:SS'
        datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        return True  # The format is correct
    except ValueError:
        return False  # The format is incorrect
    

def append_expr(key, value):
    return key + ' ' + value + ' && '

