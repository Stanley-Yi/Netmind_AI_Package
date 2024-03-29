""" 
===========
LoadMachine
===========
@file_name: LoadMachine.py
@author: Bin Liang
@date: 2024-3-1

"""


# python standard packages
import json

# python third-party packages


# import from our tools
from xyz.node.XYZNode import Node


class LoadMachine:
    """ 
    Load nodes from different data types.

    Currently, we only need to load from json files. In the future, we may load from databases or communicate with front-end and back-end.

    Parameters
    ----------
    logger : logging.Logger
        The logger to use for logging messages.
    """
    
    """ 
    TODO: 开发笔记
    可以根据不同的数据类型进行 Node 的加载。
    1. 现阶段，我们只需要使用 json 文件进行加载。
    2. 之后如果和数据库进行交互，我们可以使用数据库进行加载。
    3. 如果制作成产品，可以利用和前后端沟通的方式进行加载。
    
    所以这个功能有必要单独设计。
    """
    
    
    def __init__(self, logger):
        """
        Initialize the LoadMachine.

        Parameters
        ----------
        logger : logging.Logger
            The logger to use for logging messages.
        """
        
        self.logger = logger
    
    def __call__(self, info:str, type:str) -> list:
        """
        Load nodes from the given info and type.

        Parameters
        ----------
        info : str
            The information to load nodes from.
        type : str
            The type of the information.

        Returns
        -------
        list
            A list of nodes loaded from the info.
        """
        
        if type == "path":
            return self.load_from_path(info)

    def load_from_path(self, node_config_path):
        """
        Load nodes from a path.

        Parameters
        ----------
        node_config_path : str
            The path to load nodes from.

        Returns
        -------
        list
            A list of nodes loaded from the path.
        """
        
        node_config_list = self.get_node_config_list(node_config_path)
        
        nodes_list = []
        
        for node_config in node_config_list:
            nodes_list.append(Node(node_config))
            
        return nodes_list
    
    def get_node_config_list(self, node_config_path:str) -> str:
        """
        Get a list of node configurations from a path.

        Parameters
        ----------
        node_config_path : str
            The path to get node configurations from.

        Returns
        -------
        list
            A list of node configurations.
        """

        with open(node_config_path, "r") as f:
            node_config_list = [json.loads(line) for line in f]
        return node_config_list
    
    def save_node_config_list(self, node_config_list, node_config_path):
        """
        Save a list of node configurations to a path.

        Parameters
        ----------
        node_config_list : list
            A list of node configurations to save.
        node_config_path : str
            The path to save node configurations to.
        """

        with open(node_config_path, "w") as f:
            for node_config in node_config_list:
                f.write(json.dumps(node_config) + "\n")
