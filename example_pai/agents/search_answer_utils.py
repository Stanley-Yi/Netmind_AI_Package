from towhee import pipe, ops, DataCollection
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility, db
import pymysql
from pathlib import Path
import json
import pandas as pd
from pandas import DataFrame
import re
import numpy as np

import os
from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get(
        API_KEY),
)

MODEL = 'efficientnet_b3'
DEVICE = None  # if None, use default device (cuda is enabled if available)

# Milvus parameters
URI = 'https://in03-8d3584b60fa26a2.api.gcp-us-west1.zillizcloud.com'
TOKEN = '5c9afcc6566f3d5bee9642119d4813c5d470196431c8c42f7db177216ee5ac321824ad8ca68f2bb1cfabce896ae658e48884bbad'

# TOPK = 10  # how many images
DIM = 1536  # dimension of embedding extracted by MODEL
COLLECTION_NAME = 'duowei_education_test'
INDEX_TYPE = 'IVF_FLAT'
METRIC_TYPE = 'L2'

SQL_READER = 'netmind-rds-dev.cluster-ro-czi0esc0atmh.eu-west-2.rds.amazonaws.com'
SQL_WRITER = 'netmind-rds-dev.cluster-czi0esc0atmh.eu-west-2.rds.amazonaws.com'
SQL_PORT = 3306
SQL_USER = 'netmind'
SQL_PWD = 'NetMind@2021^159753!'
DATABASE_NAME = 'Education'
TABLE_NAME = 'question'


def load_image(x):
    if type(x) == str:
        yield '', x, ''
    else:
        for item in x:
            if item[2] == 'image':
                yield item[0], item[1].split('\'')[1], item[2]


p_embed_img = (
    pipe.input('src')
    .flat_map('src', ('sql_id', 'img_path', 'category'), load_image)
    .map('img_path', 'img', ops.image_decode())
    .map('img', 'vec', ops.image_embedding.timm(model_name=MODEL, device=DEVICE))
)

p_search_img = (
    p_embed_img.map('vec', ('search_res'), ops.ann_search.milvus_client(
        uri=URI, token=TOKEN, limit=1,
        collection_name=COLLECTION_NAME, output_fields=['text', 'sql_id']))
    .map('search_res', 'pred', lambda x: [str(Path(y[2]).resolve()) for y in x])
    .map('search_res', 'score', lambda x: [str(y[1]) for y in x])
    .map('search_res', 'mysql_id', lambda x: [str(y[3]) for y in x])
)
p_search_i = p_search_img.output('mysql_id', 'pred', 'score')

p_embed_img_vector = (
    pipe.input('src')
    .map('src', 'vec', ops.image_embedding.timm(model_name=MODEL, device=DEVICE))
)

p_search_img_vector = (
    p_embed_img_vector.map('vec', ('search_res'), ops.ann_search.milvus_client(
        uri=URI, token=TOKEN, limit=1,
        collection_name=COLLECTION_NAME, output_fields=['text', 'sql_id']))
    .map('search_res', 'pred', lambda x: [str(Path(y[2]).resolve()) for y in x])
    .map('search_res', 'score', lambda x: [str(y[1]) for y in x])
    .map('search_res', 'mysql_id', lambda x: [str(y[3]) for y in x])
)
p_search_i_vector = p_search_img_vector.output('mysql_id', 'pred', 'score')


def embed_text(x):
    respond = client.embeddings.create(
        model='text-embedding-ada-002',
        input=x,
        encoding_format="float"
    )
    return np.array(respond.data[0].embedding, dtype=np.float32)


def load_text(x):
    if type(x) == str:
        yield '', x, ''
    else:
        for item in x:
            if item[2] == 'question':
                yield item[0], item[1], item[2]


p_embed_text = (
    pipe.input('src')
    .flat_map('src', ('sql_id', 'text', 'category'), load_text)
    .map('text', 'vec', embed_text)
)

# Search pipeline
p_search_text = (
    p_embed_text.map('vec', ('search_res'), ops.ann_search.milvus_client(
        uri=URI, token=TOKEN, limit=1,
        collection_name=COLLECTION_NAME, output_fields=['sql_id', 'text']))
    .map('search_res', 'score', lambda x: [str(y[1]) for y in x])
    .map('search_res', 'mysql_id', lambda x: [str(y[2]) for y in x])
    .map('search_res', 'question', lambda x: [str(y[3]) for y in x])
)
p_search_t = p_search_text.output('mysql_id', 'question', 'score')


def process_img_search(img):
    # if the image passed in is a str or list
    dc_i = p_search_i(img)
    img_res = dc_i.to_list()
    img_df = DataFrame()
    if img_res:
        img_dict = {
            'sql': img_res[0][0],
            'image': img_res[0][1],
            'score': img_res[0][2]
        }
        img_df = pd.DataFrame(img_dict)

    return img_df


def process_img_search_vector(img):
    # if the image passed in is a np array
    dc_i = p_search_i_vector(img)
    img_res = dc_i.to_list()
    img_df = DataFrame()
    if img_res:
        img_dict = {
            'sql': img_res[0][0],
            'image': img_res[0][1],
            'score': img_res[0][2]
        }
        img_df = pd.DataFrame(img_dict)

    return img_df


def is_non_empty(img):
    if isinstance(img, np.ndarray):
        return img.size > 0
    elif isinstance(img, list):
        return len(img) > 0
    elif isinstance(img, str):
        return len(img) > 0
    else:
        return False


def question_search(txt=None, img=None, weight=(0.6, 0.4)):
    ques_df, img_df = DataFrame(), DataFrame()

    if txt:
        dc_t = p_search_t(txt)
        ques_res = dc_t.to_list()
        if ques_res:
            ques_dict = {
                'sql': ques_res[0][0],
                'question': ques_res[0][1],
                'score': ques_res[0][2]
            }
            ques_df = pd.DataFrame(ques_dict)

    if is_non_empty(img):
        if type(img) == np.ndarray:
            img_df = process_img_search_vector(img)
        elif type(img) == list:
            if len(img) > 1:
                dfs = []
                for i in img:
                    cur_df = process_img_search(i)
                    if not cur_df.empty:
                        dfs.append(cur_df)
                all_dfs_combined = pd.concat(dfs)
                all_dfs_combined['score'] = all_dfs_combined['score'].astype(float)

                df_sorted = all_dfs_combined.sort_values(by=['sql', 'score'])
                img_df = df_sorted.drop_duplicates(subset='sql', keep='first')
            else:
                img_df = process_img_search(img[0])
        else:
            img_df = process_img_search(img)

    if not ques_df.empty and not img_df.empty:
        # V1
        merged_df = pd.merge(img_df, ques_df, on='sql', suffixes=('_img', '_txt'))

        if merged_df.empty:  # no intersection
            weighted_txt = weight[0] * ques_df['score'].astype(float).iloc[0]
            weighted_img = weight[1] * img_df['score'].astype(float).iloc[0]

            return ques_df.iloc[0] if weighted_img >= weighted_txt else img_df.iloc[0]

        merged_df['score_total'] = (weight[0] * merged_df['score_txt'].astype(float) + weight[1] * merged_df[
            'score_img'].astype(float)) / 2
        result_df = merged_df.sort_values(by='score_total').iloc[0]

        return result_df
    elif not ques_df.empty:
        return ques_df.iloc[0]
    elif not img_df.empty:
        return img_df.iloc[0]

    return DataFrame()