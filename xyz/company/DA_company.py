""" 
==========
DA_company
==========
@file_name: DA_company.py
@author: Bin Liang
@date: 2024-3-1
根据北京团队所做的一些 twitter 工具，进行 自动化的 数据分析
"""


from xyz.company.Company import Company
from xyz.node.Node import Node


if __name__ == "__main__":
    
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
    staffs = [data_spider, data_process, data_analysis, report_writer]
    tda_company = Company(staffs = staffs)
    
    # Step 3: 运行公司的功能
    task = "" 
    tda_company.working(task=task)
    
    tda_company.save()
    
    # ======================== 再次读取
    
    # company_config = {}
    # tda_company = Company(company_config)
    
    # task = "" 
    # tda_company.working(task=task)
    
    