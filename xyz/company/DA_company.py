""" 
==========
DA_company
==========
@file_name: DA_company.py
@author: Bin Liang
@date: 2024-3-1
根据北京团队所做的一些 twitter 工具，进行 自动化的 数据分析
"""

# python standard packages
import os 
import threading

# python third-party packages


# import from our operation
from xyz.company.Company import Company
from xyz.node.XYZNode import Node
from xyz.parameters import args
from xyz.utils.APIWrapTool import APIWrapTool

# Step 0: 特殊的函数
def special_function():
    pass

if __name__ == "__main__":
    
    os.environ["OPENAI_API_KEY"] = args.key
    
    # Step 0: 把需要特殊执行的 利用 多线程开启 api
    
    # 0-1: 利用 twitter api 获取数据的函数
    special_function_thread = APIWrapTool(special_function, "This is a special function",
                                          host="127.0.0.1", port=8501)
    api_thread = threading.Thread(target=special_function_thread.run_api())
    api_thread.start()
    
    # ======================== 第一次创建    

    # Step 1: 配置 需要的功能 的Node
    data_spider_config = {}
    data_spider = Node(data_spider_config)
    
    data_process_config = {}
    data_process = Node(data_process_config)

    data_analysis_config = {}
    data_analysis = Node(data_analysis_config)
    
    report_writer_config = {}
    report_writer = Node(report_writer_config)
    
    # Step 2: 配置 公司的功能
    nodes_list = [data_spider, data_process, data_analysis, report_writer]
    twitter_data_analysis_company = Company(nodes_list = nodes_list)
    
    # Step 3: 运行公司的功能
    task = "" 
    twitter_data_analysis_company.working(task=task)
    
    twitter_data_analysis_company.save()
    
    # ======================== 再次读取
    
    company_config = {}
    twitter_data_analysis_company = Company(company_config)
    
    task = "" 
    twitter_data_analysis_company.working(task=task)
    
    