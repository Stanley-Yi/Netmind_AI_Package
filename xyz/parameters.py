""" 
==========
parameters
==========
@file_name: parameters.py
@date: 2024-3-8
@author: Bin Liang
This is a temporary client for now. We need a interface to setup the keys, and save place
"""


import argparse
from xyz.utils.logger import create_logger


# parser = argparse.ArgumentParser(description='BlackSheep Client')
# parser.add_argument('--key', type=str, default='', help='The key for the client')
# parser.add_argument('--save_folder', type=str, default='saved_nodes', help='The place for saving the configuration of the nodes')
# args = parser.parse_args()

# logger = create_logger(f"{args.save_folder}/logs")

logger = create_logger(f"./logs")


# ==================== 我们初始化一个 core_agent
from xyz.utils.llm.core_agent import CoreAgent
core_agent = CoreAgent()
