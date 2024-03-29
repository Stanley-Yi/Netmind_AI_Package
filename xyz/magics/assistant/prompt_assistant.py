"""
===============
PromptAssistant
===============
@file_name: prompt_assistant.py
@author: Bin Liang
@date: 2024-3-14
"""

from typing import Any, List

from tqdm.auto import tqdm

from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent
from xyz.magics.assistant.prompts import default_generators, default_modifiers


class PromptsCartridge(Agent):

    def __init__(self, core_agent):
        super().__init__(core_agent=core_agent)

        self.name = "PromptsCartridge"
        self.description = {
            "input": "",
            "output": "",
            "description": ""
        }
        self.parameters = {}

    def flowing(self, user_input: str, strategy_list: List = None) -> List:

        results = []

        prompts_list = self.strategy2prompt(strategy_list=strategy_list)

        process_bar = tqdm(prompts_list, desc="Processing prompts", leave=False)

        for prompt in prompts_list:
            local_llm_agent = LLMAgent(template=prompt, core_agent=self.core_agent, inner_multi=False, stream=False)
            local_result = local_llm_agent(content=user_input)
            results.append(local_result)
            process_bar.update(1)

        return results

    def strategy2prompt(self, strategy_list: List) -> List:
        """
        A strategy to generate prompts for the user.

        Parameters
        ----------
        strategy_list
            A list of prompts, by default None.

        Returns
        -------
        List
            A list of prompts.
        """

        prompts = []

        for strategy in strategy_list:
            local_prompt = [{"role": "system", "content": strategy},
                            {"role": "user", "content": "{content}"}]
            prompts.append(local_prompt)

        return prompts


class PromptAssistant(Agent):
    """
    PromptAssistant is a class to help the user to generate or modify prompts.
    """

    def __init__(self, core_agent=None) -> None:
        super().__init__(core_agent)

    def flowing(self, task: str, prompt: str = None, strategy_list: List = None, show: bool = True) -> Any:

        prompt_cartridge = PromptsCartridge(core_agent=self.core_agent)

        if prompt is None:

            user_input = f"My task is {task}. Please help me to make some good prompts."
            if strategy_list is None:
                results_prompt = prompt_cartridge(user_input=user_input, strategy_list=default_generators)
            else:
                results_prompt = prompt_cartridge(user_input=user_input, strategy_list=strategy_list)

        else:

            user_input = f"My task is {task}. And my current prompt is: {prompt}\n Please help me to make it better!"

            if strategy_list is None:
                results_prompt = prompt_cartridge(user_input=user_input, strategy_list=default_generators)
            else:
                results_prompt = prompt_cartridge(user_input=user_input, strategy_list=strategy_list)

        if show:
            for result in results_prompt:
                print(result)

        return results_prompt

