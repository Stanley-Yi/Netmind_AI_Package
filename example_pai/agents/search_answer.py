"""
=============
search_answer
=============
@file_name: search_answer.py
@author: Bin Liang, Tianlei Shi
@date: 2024-3-22
"""


import pymysql
from ast import literal_eval

from xyz.node.agent import Agent
from xyz.parameters import openai_agent

from example_pai.agents.search_answer_utils import question_search


SQL_READER = 'netmind-rds-dev.cluster-ro-czi0esc0atmh.eu-west-2.rds.amazonaws.com'
SQL_WRITER = 'netmind-rds-dev.cluster-czi0esc0atmh.eu-west-2.rds.amazonaws.com'
SQL_PORT = 3306
SQL_USER = 'netmind'
SQL_PWD = 'NetMind@2021^159753!'
DATABASE_NAME = 'Education'
TABLE_NAME = 'question'
COL = 'knowledge_points'
TOPK = 5

mapping = {
            'A': 0,
            'B': 1,
            'C': 2,
            'D': 3,
            'E': 4,
            '1': 0,
            '2': 1,
            '3': 2,
            '4': 3,
        }


class SearchAnswer(Agent):
    """
    A class for searching the answer to a question.

    Parameters
    ----------
    question : str
        The question to search the answer for.
    """

    def __init__(self):
        super().__init__(openai_agent)

        self.set_name("SearchAnswer")
        self.set_description("This is a teacher which can guide the user to search similar problem.")
        self.set_parameters({"question": {"type": "str", "description": "The question here which need be researched."},
                             "images": {"type": "str", "description": "The image of this question."},
                             "course": {"type": "str", "description": "The course about this question."}})

        # 配置我们的 memory agent

    def flowing(self, question: str, course: str, images=None):
        """
        流程1: 根据 ocr 结果进行搜索

        TODO: 1: 利用向量数据库进行范围
        TODO: 2: 对向量数据中数据储存的字段进行一个设计：
        TODO: 3: 如果数据库中的 process 是空字符串，需要我们调用 self._generate_process 进行补全
                并且保存到数据库中
        """
        answer, process, knowledge_point = None, None, None
        try:
            result = question_search(question, images)

            if float(result['score']) > 0.5:
                print('No similar problem in our database')
                return {}

            # get problem in mysql via id
            problem = None
            connection = pymysql.connect(host=SQL_READER, port=SQL_PORT, user=SQL_USER, password=SQL_PWD,
                                         database=DATABASE_NAME)
            try:
                with connection.cursor() as cursor:
                    sql = f"SELECT * FROM {TABLE_NAME} WHERE id = %s"
                    cursor.execute(sql, (result['sql'],))

                    problem = cursor.fetchone()
            finally:
                connection.close()

            knowledge_point = problem[8]
            answer = problem[6]
            opt = literal_eval(problem[7])

            if opt:
                index = mapping.get(answer.upper(), None)
                if index is not None and index < len(opt):
                    answer += ': ' + opt[index]

            # problem 里面应该是有的
            process = ""  # 给的数据里没有 process

        except Exception as e:
            print(e)

        return {"question": question,
                "answer": answer,
                "process": process,
                "course": course,
                "knowledge_point": knowledge_point}

