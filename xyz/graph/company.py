"""
=====
Graph
=====
@file_name: graph.py
@author: Bin Liang
@date: 2024-04-07
    This is a class for graph
"""


__all__ = ["AutoCompany"]

from typing import Any

from xyz.node.agent import Agent
from xyz.elements.assistant.manager_assistant import ManagerAssistant
from xyz.utils.llm.openai_client import OpenAIClient


class AutoCompany(Agent):
    """
    主要功能
    1. input format
    2. manager 决定流程
        i. Manger 在 company 执行任务之前，就决定 edges 优先这个版本的流程
        ii. 在运行中，根据 edges 去选择下一个
    3. 对 Manager 的分析结果进行理解和执行

    使用方式
    1. 创建一个 AutoCompany 对象
    2. 添加一组 Agents
    3. 给定一个 Task
    4. 运行 AutoCompany，就开始进行 完整的流程：
        理解任务，分配任务，执行任务

    这个自驱动的 Company 有什么用？
    1. 自动化进行 多智能体 协作 （针对开发者，没什么帮助。针对非开发者，挺有意思的）
    2. 如果有一套合适的 Agents 组织结构，可以管理一个非常大的 AI-Society，黑盒能力可以解决更多的问题

    设计记录
    在执行任务之前，先获取当前的 task，和手下所有员工的信息。
    1. 判断这些员工是否可以解决当前任务
    2. 开始列计划，安排工作流程。
    3. 开始执行任务
        1. 选择一个 Agent 进行执行。 输入：当前的任务，需要这个 Agent 做的事情 输出：Agent 的执行结果
        2. 根据 Agent 的执行结果，进行下一个 Agent 的选择
        3. Manager 对输出进行一些处理
        4. 重复 1-3，直到任务结束

    work plan 是什么格式？
    一个 sequence ：
    [
        {"name": "", "sub_task": "", "position" : ""},
        {"name": "", "sub_task": "", "position" : ""},
        {"name": "", "sub_task": "", "position" : ""},
    ]
    一个 graph ：
    Node=Agents_List
    由 manager 生成 Edge
    在执行的时候，由 Manager 根据 Edge 选择下一个 Agent，循环这个过程来执行任务

    疑问：
    1. Manager 需不需要参与到每一个环节里？
    2. 最终的答案需不需要 Manager 进行总结？

    简单版本：
    1. 线性执行，只按照给出的顺序执行
    2. 无法进行 条件判断
    3. 无法进行 循环

    复杂版本：
    1. work plan 可以是一个图，可以有多个分支
    2. 可以有条件判断
    3. 可以有循环
    """
    llm_client: OpenAIClient
    manager: ManagerAssistant
    agents: list

    def __init__(self, llm_client: OpenAIClient) -> None:
        super().__init__()

        self.llm_client = llm_client
        self.manager = ManagerAssistant(llm_client)
        self.agents = []

    def flowing(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def add_agent(self, agent: list) -> None:
        self.agents.append(agent)

    def read_work_plan(self, work_plan):
        raise NotImplementedError

    def create_work_plan(self):
        raise NotImplementedError

    def execute_step(self):
        raise NotImplementedError

