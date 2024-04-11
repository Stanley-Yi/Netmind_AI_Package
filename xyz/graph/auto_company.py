"""
=====
Graph
=====
@file_name: agent_graph.py
@author: Bin Liang
@date: 2024-04-07
    This is a class for graph
"""

__all__ = ["AutoCompany"]

import logging
import inspect
import os
import time
import re
import json
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
    和一个 edge：
    {
        "node_1" : ["node_x", "node_y"],
        ...
    }
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
    agents: dict
    agents_info: str
    graph: dict

    def __init__(self, llm_client: OpenAIClient, logger_path=None) -> None:
        super().__init__()

        self.graph = {}
        self.agents = {}
        self.agents_info = ""
        self.llm_client = llm_client
        self.manager = ManagerAssistant(llm_client)

        self.logger = self.create_logger(logger_path)

    def flowing(self, user_input, work_plan: dict = None) -> Any:

        # Step 1: Manager 分析当前任务
        task_analysis = self.manager.analyze_task(user_input)
        self.logger.info("=======Start=========", extra={"step": "Task Analysis",
                                                         "agent": "Manager-Assistant"})
        self.stream_show(task_analysis)
        # TODO: 解决不了直接结束

        # Step 2: Manager 开始对任务进行分配，并且生成 work plan
        agents_info = self.get_agents_info()
        if work_plan is None:
            work_plan_str = self.manager.create_work_plan(task_analysis, agents_info)
            work_plan = self.read_work_plan(work_plan_str)
        self.logger.info("=======Work-Plan=========", extra={"step": "Work Plan",
                                                             "agent": "Manager-Assistant"})
        self.stream_show(str(work_plan))

        # Step 3: Manager 开始执行 work plan
        solving_history = self.execute_work_plan(task=task_analysis, work_plan=work_plan)

        # Step 4: 制作总结
        summary_response = self.manager.summary(solving_history)
        self.logger.info("=======Summary=========", extra={"step": "Summary",
                                                           "agent": "Manager-Assistant"})
        self.stream_show(summary_response)

        solving_record = ("User Input: " + user_input + "\n" + task_analysis
                          + solving_history + summary_response)

        return work_plan, solving_record

    def add_agent(self, agents: list) -> None:
        for agent in agents:
            self.agents[agent.information["name"]] = agent

    def get_agents_info(self):

        agents_info = "In this company, we have the following agents:\n"

        for agent in self.agents:
            agents_info += (f"## ----------\nName: {agent.information['name']}\n"
                            f"Description: {agent.information['description']}\n"
                            f"Input Type: {agent.input_type}\n"
                            f"Output Type{agent.output_type}\n## ----------\n\n")

        return agents_info

    @staticmethod
    def read_work_plan(work_plan_str: str):

        matches = re.findall(r'```(.*?)```', work_plan_str, re.DOTALL)
        working_graph = {}

        # 将提取出的字符串转换为Python的字典
        agents = [json.loads(match) for match in matches]

        for agent in agents:
            working_graph[agent["name"]] = agent

        return working_graph

    def execute_work_plan(self, task: str, work_plan: dict):

        start_agent = None
        end_agent = None
        working_history = ""

        # Step 1: 选择第一个 Agent
        for agent_info in work_plan:
            if agent_info["position"] == "start":
                start_agent = agent_info["name"]
            elif agent_info["position"] == "end":
                end_agent = agent_info["name"]
                agent_info["name"]["next"] = "Finish"

        assert start_agent is not None, "No start agent found in the work plan"
        assert end_agent is not None, "No end agent found in the work plan"

        current_point = start_agent
        current_content = task
        while current_point != "Finish":

            self.logger.info("-------------", extra={"step": f"{work_plan[current_point]['sub_task']}",
                                                     "agent": current_point})

            # Step 0: Get the agent object
            execute_agent = self.agents[current_point]
            # Step 1: Execute the agent
            # TODO: 进行  Input Format 的转换
            response = execute_agent(current_content)
            current_response = self.stream_show(response)

            # Step 2: Manager do the small summary
            next_list_info = self.get_next_list_info(work_plan[current_point])
            current_summary = self.manager.summary_step(working_history=working_history,
                                                        current_response=current_response,
                                                        next_list_info=next_list_info)

            # Step 3: Log the information
            current_summary_content = self.stream_show(current_summary)

            # Step 4: Update the working history
            working_history += current_summary + "\n"

            # Step 5: Update the current point
            next_name = self.get_next_name(current_summary_content)
            if next_name in work_plan:
                current_point = next_name
            else:
                current_point = "Finish"
                self.logger.info("The work plan is finished", extra={"step": "Finish",
                                                                     "agent": "None"})

            # Step 6: 迭代下一轮的输入
            current_content = current_response

        return working_history

    def stream_show(self, response):

        full_content = ""
        if inspect.isgenerator(response):
            for word in response:
                self.logger.process(word, extra={"step": "in progress", "agent": "None"})
                full_content += word
        else:
            full_content = response
            self.logger.info(response)

        self.logger.process("\n", extra={"step": "in progress", "agent": "None"})

        return full_content

    def get_next_list_info(self, work_step):

        next_info = f"Next Agents: \n\n"
        for agent_name in work_step['next']:
            agent = self.agents[agent_name]
            next_info += (f"## ----------\nName: {agent.information['name']}\n"
                          f"Description: {agent.information['description']}\n"
                          f"Input Type: {agent.input_type}\n"
                          f"Output Type{agent.output_type}\n## ----------\n\n")

        return next_info

    @staticmethod
    def get_next_name(current_summary_content):

        next_name = re.findall(r'\|\|\|(.*?)\|\|\|', current_summary_content, re.DOTALL)
        if next_name is None:
            return "Finish"
        else:
            return next_name.group(1)

    @staticmethod
    def create_logger(logger_path=None):

        class ColoredFormatter(logging.Formatter):
            RED = '\033[31m'
            CYAN = '\033[36m'
            GREEN = '\033[32m'
            RESET = '\033[0m'

            def format(self, record):
                record.step = self.RED + str(record.step) + self.RESET
                record.agent = self.CYAN + str(record.agent) + self.RESET
                record.msg = self.GREEN + str(record.msg) + self.RESET
                return super().format(record)

        if logger_path is None:
            current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
            os.makedirs("logs", exist_ok=True)
            local_path = f"logs/tmp_log_{current_time}.log"
        else:
            local_path = logger_path
            logger_path = None

        PROCESS_LEVEL_NUM = 25
        logging.addLevelName(PROCESS_LEVEL_NUM, "PROCESS")

        def process(self, message, *args, **kws):
            if self.isEnabledFor(PROCESS_LEVEL_NUM):
                self._log(PROCESS_LEVEL_NUM, message, args, **kws)

        logging.Logger.process = process

        class StreamHandlerNoNewline(logging.StreamHandler):
            def emit(self, record):
                if record.levelno == PROCESS_LEVEL_NUM:
                    msg = record.getMessage()
                else:
                    msg = self.format(record)
                    msg += "\n"
                if self.stream is None:
                    self.stream = self._open()
                self.stream.write(msg)
                self.stream.flush()

        class FileHandlerNoNewline(logging.FileHandler):
            def emit(self, record):
                if record.levelno == PROCESS_LEVEL_NUM:
                    msg = record.getMessage()
                else:
                    msg = self.format(record)
                    msg += "\n"
                if self.stream is None:
                    self.stream = self._open()
                self.stream.write(msg)
                self.stream.flush()

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        file_handler = FileHandlerNoNewline(local_path)
        file_handler.setLevel(logging.INFO)
        console_handler = StreamHandlerNoNewline()
        console_handler.setLevel(logging.INFO)

        formatter_console = ColoredFormatter('Step: %(step)s - Agent: %(agent)s - %(message)s')
        formatter_file = logging.Formatter('Step: %(step)s - Agent: %(agent)s - %(message)s')
        console_handler.setFormatter(formatter_console)
        file_handler.setFormatter(formatter_file)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger
