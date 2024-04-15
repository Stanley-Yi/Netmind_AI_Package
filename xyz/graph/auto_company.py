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
from xyz.elements.assistant.input_format_assistant import InputFormatAssistant
from xyz.utils.llm.openai_client import OpenAIClient


class AutoCompany(Agent):
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
        self.input_format_agent = InputFormatAssistant(llm_client)

        self.logger = self.create_logger(logger_path)

    def flowing(self, user_input, work_plan: dict = None) -> Any:

        # Step 1: Manager 分析当前任务
        agents_info = self.get_agents_info()
        task_analysis = self.manager.analyze_task(user_input=user_input, agents_info=agents_info)
        self.logger.info("=======Start=========", extra={'step': "Task Analysis",
                                                         'agent': "Manager-Assistant"})
        task_analysis = self.stream_show(task_analysis)
        if "NO-WE-CAN-NOT" in task_analysis:
            return None

        # Step 2: Manager 开始对任务进行分配，并且生成 work plan
        if work_plan is None:
            self.logger.info("=======Work-Plan=========", extra={'step': "Work Plan",
                                                                 'agent': "Manager-Assistant"})
            work_plan_str = self.manager.create_work_plan(task_analysis, agents_info)
            work_plan_str = self.stream_show(work_plan_str)
            work_plan = self.read_work_plan(work_plan_str)

        # Step 3: Manager 开始执行 work plan
        solving_history = self.execute_work_plan(user_input=user_input, task=task_analysis, work_plan=work_plan)

        # Step 4: 制作总结
        summary_response = self.manager.summary(solving_history)
        self.logger.info("=======Summary=========", extra={'step': "Summary",
                                                           'agent': "Manager-Assistant"})
        summary_response = self.stream_show(summary_response)

        solving_record = ("User Input: " + user_input + "\n" + task_analysis
                          + solving_history + summary_response)

        self.logger.info("=======Finish=========\n\t\tSee you next time!!!", extra={'step': "Finish",
                                                                                    'agent': "Netmind_AI_XYZ"})

        return work_plan, solving_record

    def execute_work_plan(self, user_input: str, task: str, work_plan: dict):

        working_history = ""

        # Prepare: Choose the start agent and end agent
        positions = {agent_info['position']: agent_info['name'] for agent_info in work_plan.values()}
        start_agent = positions.get('start')
        end_agent = positions.get('end')

        assert start_agent is not None, "No start agent found in the work plan"
        assert end_agent is not None, "No end agent found in the work plan"

        current_point = start_agent
        current_content = (f"The user input is: {user_input}\n\n"
                           f"The task analysis is: {task}\n\n"
                           f"The Plan is: \n\n{json.dumps(work_plan)}\n\n"
                           f"Now, we need let the first agent to start the work. "
                           f"We must call the first function, and get the parameters from the information above.")

        while current_point != "ErrorStop":

            self.logger.info("-------------", extra={'step': f"In Company Progress: {work_plan[current_point]['sub_task']}",
                                                     'agent': f"Company Agent: {current_point}"})
            # Step 0: Get the agent object
            execute_agent = self.agents[current_point]

            # Step 1: Execute the agent
            self.logger.info("-------------\nI am communicating with this agent and arranging tasks for him. Please wait."
                             "\n-------------", 
                             extra={'step': "Analysis the parameters", 'agent': "Manager-Assistant"})
            format_current_content = self.input_format_agent(input_content=current_content,
                                                             functions_list=[execute_agent.information])
            response = execute_agent(**format_current_content)
            current_response = self.stream_show(response)

            if work_plan[current_point]['position'] == "end":
                working_history += current_point + ":" + current_response + "\n\n"
                self.logger.info("The work plan is finished", extra={'step': "Finish",
                                                                     'agent': "None"})
                break

            # Step 2: Manager do the small summary
            next_list_info = self.get_next_list_info(work_plan[current_point])
            current_summary = self.manager.summary_step(working_history=working_history,
                                                        current_response=current_response,
                                                        next_list_info=next_list_info)

            # Step 3: Log the information
            self.logger.info("-------Step Summary------", extra={'step': f"Summarize this step",
                                                                 'agent': f"Manager-Assistant"})
            current_summary_content = self.stream_show(current_summary)

            # Step 4: Update the working history
            working_history += current_point + ":" + current_summary_content + "\n\n"
            self.input_format_agent.add_history([{"role": "assistant", "content": current_summary_content}])

            # Step 5: Update the current point
            next_name = self.get_special_part(pattern="next-employee", content=current_summary_content)
            name = json.loads(next_name)
            next_name = name['name']
            if next_name in work_plan:
                current_point = next_name
                current_content = current_response + self.get_special_part(pattern="next-step",
                                                                           content=current_summary_content)
            else:
                current_point = "ErrorStop"
                self.logger.info("This task is terminate with some error.", extra={'step': "Terminate",
                                                                                   'agent': "AutoSystem"})

        return working_history

    def read_work_plan(self, work_plan_str: str):

        matches = self.get_special_part("working-plan", work_plan_str)
        working_graph = {}

        matches = re.sub(r'(?<!\\)\\(?!\\)', '\\\\\\\\', matches)
        agents = json.loads(matches)

        for i, agent in enumerate(agents):
            if i == 0:
                agent["position"] = "start"
            elif i == len(agents) - 1:
                agent["position"] = "end"
            else:
                agent["position"] = "in-progress"

            working_graph[agent["name"]] = agent

            if i != 0:
                working_graph[agents[i - 1]["name"]]["next"] = [agent["name"]]

        return working_graph

    def add_agent(self, agents: list) -> None:
        for agent in agents:
            self.agents[agent.information["function"]["name"]] = agent

    def get_agents_info(self):

        agents_info = "In this company, we have the following agents:\n"

        for name, agent in self.agents.items():
            agents_info += (f"## ----------\nName: {name}\n"
                            f"Description: {agent.information['function']['description']}\n"
                            f"Input Type: {agent.input_type}\n"
                            f"Output Type{agent.output_type}\n## ----------\n\n")

        return agents_info

    def get_next_list_info(self, work_step):

        next_info = f"Next Agents: \n\n"
        for agent_name in work_step['next']:
            agent = self.agents[agent_name]
            next_info += (f"## ----------\nName: {agent_name}\n"
                          f"Description: {agent.information['function']['description']}\n"
                          f"Input Type: {agent.input_type}\n"
                          f"Output Type{agent.output_type}\n## ----------\n\n")

        return next_info

    @staticmethod
    def get_special_part(pattern: str, content: str) -> str:

        pattern = "\|\|\|" + pattern
        # 使用正则表达式提取`special_char special_char`之间的内容
        pattern = pattern + '(.*?)' + pattern
        match = re.search(pattern, content, re.DOTALL)

        if match:
            # 使用group(1)获取第一个括号内匹配的内容，并使用strip()去除前后的空白字符
            result = match.group(1).strip()
        else:
            result = ""

        return result

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
                    try:
                        msg = self.format(record)
                        msg += "\n"
                    except:
                        msg = record.getMessage()
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
                    try:
                        msg = self.format(record)
                        msg += "\n"
                    except:
                        msg = record.getMessage()
                        msg += "\n"
                if self.stream is None:
                    self.stream = self._open()
                self.stream.write(msg)
                self.stream.flush()

        # logger = logging.getLogger()
        logger = logging.getLogger("Assistant")
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

    def stream_show(self, response):

        full_content = ""
        if inspect.isgenerator(response):
            for word in response:
                self.logger.process(word, extra={'step': "in progress", 'agent': "None"})
                full_content += word
        else:
            full_content = response
            self.logger.info(response, extra={'step': "in progress", 'agent': "None"})

        self.logger.process("\n", extra={'step': "in progress", 'agent': "None"})

        return full_content
