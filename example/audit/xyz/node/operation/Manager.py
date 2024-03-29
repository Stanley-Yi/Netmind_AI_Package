""" 
=======
Manager
=======
@file_name: Manager.py
@author: Bin Liang
@date: 2024-3-1

"""


# python standard packages


# python third-party packages


# import from our tools
from xyz.node.basic.llm_agent import LLMAgent


class Manager(LLMAgent):
    """ 
    TODO: 开发笔记
    需要有的功能：
    
    1. 和其他的 assistant 进行交互
    2. 能够修改其他 assistant 的prompts 进行迭代升级，或许可以利用 autoprompts 这个项目
    3. 能够获取所有 assistant 当前的状态和信息，进行任务的分配和调度
    4. 能够判断当前任务的进程，是否已经结束。
    
    设计的思路：
    1. 是否需要针对每一个任务单独由用户定义
    2. 是否可以是一个通用的，我们用一套的 prompts 就能给所有的任务进行使用。
    
    如果是 2. 的话，可以大大减少用户的工作量，是我们的系统更加的易用，但是有可能性能会不够好。
    是否可以结合 1. 2.，在通用的基础上，增加一些可选的可以自定义的内容。
    """
    
    def __init__(self, config):
        super().__init__(config)
        # TODO：这个 manager 相当于是一个 特殊的管理者，可以进行特殊的操作
        raise NotImplementedError

    def __call__(self, *args, **kwds):
        raise NotImplementedError

    def run(self, content:str) -> str:
        raise NotImplementedError

    def save(self) -> None:
        raise NotImplementedError
    