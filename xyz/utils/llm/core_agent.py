"""
=========
CoreAGent
=========
@file_name: core_agent.py
@author: Netmind.AI BlackSheep team 
@date: 2024-1-10 
To define the BlackSheep-Agent(The BasicCLass of Agent)
"""

# python standard packages
import time
import traceback
from typing import Generator, List

# python third-party packages
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

# import from our operation
# from xyz.parameters import logger


class CoreAgent:

    def __init__(self, llm: str = "gpt-4-1106-preview", temperature: float = 0, logger = None):
        """Initializes the agent.

        Parameters
        ----------
        llm : str, optional
            the openai model name for this llm, by default "gpt-4-1106-preview"
        temperature : int, optional
            the generation parameters, by default 0
        logger : logger object, optional
            which logger we will use to store all the logs, by default logger
        """

        self.client = OpenAI()

        self.llm = llm
        self.temperature = temperature

        self.logger = logger

    def run(self, messages: List, tools: List = []) -> ChatCompletion | Stream[ChatCompletionChunk]:
        """
        Run the agent with the given messages.

        Parameters
        ----------
        messages : list
            A list of messages to be processed by the agent.
        tools : list, optional
            A list of tools to be used by the agent, by default [].

        Returns
        -------
        str
            The agent's response to the messages.

        Raises
        ------
        Exception
            If there is an error while processing the messages.
        """

        if tools:
            tool_choice = "auto"
        else:
            tool_choice = "none"

        get_response_signal = False
        count = 0
        while not get_response_signal and count < 10:
            try:
                # In OpenAI's api, if we request with tools == [], it will make an error
                if tool_choice == "auto":
                    response = self.client.chat.completions.create(
                        model=self.llm,
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        temperature=self.temperature,
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.llm,
                        messages=messages,
                        temperature=self.temperature,
                    )
                get_response_signal = True

                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                this_time_price = self.get_oai_fees(self.llm, prompt_tokens, completion_tokens)
                # TODO: We do not compute the price for now, but we can add this feature in the future

                return response

            except Exception as e:
                count += 1
                error_message = str(traceback.format_exc())
                print(f"The error: {error_message}")
                print(f"The messages: {messages}")
                time.sleep(2)

    def stream_run(self, messages: List) -> Generator[str, None, None]:
        """
        Run the agent with the given messages in a streaming manner.

        Parameters
        ----------
        messages : list
            A list of messages to be processed by the agent.

        Yields
        ------
        str
            The agent's response to the messages, yielded one piece at a time.

        Raises
        ------
        Exception
            If there is an error while processing the messages.
        """
        # 流式输出，为后续产品化作准备

        get_response_signal = False
        count = 0
        answer = ""
        while not get_response_signal and count < 10:
            try:
                for response in self.client.chat.completions.create(
                        model=self.llm,
                        messages=messages,
                        temperature=self.temperature,
                        stream=True,
                        timeout=5
                ):

                    if response.choices[0].delta.content == None:
                        messages.append({"role": "assistant", "content": answer})
                        get_response_signal = True
                        return "--Finish--"
                    else:
                        text = response.choices[0].delta.content
                        yield text
                        answer += text
            except Exception as e:
                count += 1
                error_message = str(traceback.format_exc())
                time.sleep(2)
                logger.error(f"The error: {error_message}")

        answer = response.choices[0].message.content

        return answer

    @staticmethod  # dollars per 1k tokens, REF: https://openai.com/pricings Source: He Yan
    def get_oai_fees(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculate the fees for using OpenAI models based on the model name, prompt tokens, and completion tokens.

        Parameters:
        model_name (str): The name of the OpenAI model.
        prompt_tokens (int): The number of tokens used for the prompt.
        completion_tokens (int): The number of tokens used for the completion.

        Returns:
        float: The calculated fee for using the OpenAI model.

        Raises:
        ValueError: If the model name is unknown.

        """

        openai_price = {
            "gpt-4": {
                "prompt": 0.03,
                "completion": 0.06
            },
            "gpt-4-32k": {
                "prompt": 0.06,
                "completion": 0.12
            },
            "gpt-4-1106-preview": {
                "prompt": 0.01,
                "completion": 0.03
            },
            "gpt-4-0125-preview": {
                "prompt": 0.01,
                "completion": 0.03
            },
            "gpt-3.5-turbo": {
                "prompt": 0.0015,
                "completion": 0.002
            },
            "gpt-3.5-turbo-16k": {
                "prompt": 0.003,
                "completion": 0.004
            }
        }

        if model_name.startswith("gpt-4-32k"):
            model_name = "gpt-4-32k"
        elif model_name.startswith("gpt-4-1106"):
            model_name = "gpt-4-1106-preview"
        elif model_name.startswith("gpt-4-0125"):
            model_name = "gpt-4-0125-preview"
        elif model_name.startswith("gpt-4"):
            model_name = "gpt-4"
        elif model_name.startswith("gpt-3.5-turbo-16k"):
            model_name = "gpt-3.5-turbo-16k"
        elif model_name.startswith("gpt-3.5-turbo"):
            model_name = "gpt-3.5-turbo"
        else:
            raise ValueError(f"Unknown model name {model_name}")
        if model_name not in openai_price:
            return -1
        fee = (openai_price[model_name]["prompt"] * prompt_tokens + openai_price[model_name][
            "completion"] * completion_tokens) / 1000

        return fee
