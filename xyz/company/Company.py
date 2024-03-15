""" 
=======
Company
=======
@file: Company.py
@author: Bin Liang
@date: 2023-2-29

"""


# python standard packages


# python third-party packages


# import from our operation
from xyz.node.XYZNode import Node
from xyz.node.basic.Edge import Edge


class Company:
    
    def __init__(self, nodes_list:list, auto=False ):
        """
        TODO: 考虑一下同步 异步的事情
        自动/手动
        feedback 自我改进
        """
        
        self.auto = auto
        self.node_list = {}
        
        for i, node in enumerate(nodes_list) :
            if i == 0:
                node.set_role("start")
            elif i == len(nodes_list) - 1:
                node.set_role("end")
            else:
                node.set_role("process")
            self.node_list[node.name] = node
            
        if not auto:
            self.start = nodes_list[0]
            if len(nodes_list) == 1:
                nodes_list[0].set_role("end")
            else:
                for i in range(len(nodes_list) - 1):
                    self._build_edge(nodes_list[i], nodes_list[i+1])
                
        # TODO: 复杂的 graph 应该是一个有向环图，这里我们暂时不考虑这个问题
        # TODO: 如果是有向环图，我们可以用把这里的 value 变成一个 字典。
        self.edge = {}

    def __str__(self, *args, **kwds):
        raise NotImplementedError
    
    def working(self, task:str) -> None:
        
        if not self.auto:
            result = self._artificial_working(task)
        else:
            raise TypeError("We do not complete the task automatically. Please set auto=False.")
        return result
    
    def _build_edge(self, node_1:Node, node_2:Node) -> None:
        
        self.edge[node_1.name] = Edge(node_1, node_2)
        
    def _artificial_working(self, task:str) -> None:
        
        full_process = []
        node = self.start
        response = node.flowing(task)
        step = 1
        full_process.append({
            "node": node.name,
            "response": response,
            "step": f"step_{step}"
        })
        
        while node.company_role != "end":
            
            step += 1
            
            # TODO: 如果是有向环图，或者每个 node 有多个 edge 链接，这里需要一个 manager 进行下一个 node 的挑选。
            node = self.edge[node.name].back_node
            
            sub_task_parameters = self.edge[node.name].bridge(response)
            response = node.flowing(task=task, **sub_task_parameters)
            full_process.append({
                "node": node.name,
                "response": response,
                "step": f"step_{step}"
            })
            # TODO: 这里其实可以做一个 总结 Agent，去把全过程整理成一个长回答
            result = response

        return result, full_process
            
    def save(self) -> None:
        raise NotImplementedError
    
    
    