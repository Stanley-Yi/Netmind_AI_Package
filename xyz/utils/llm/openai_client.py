"""
=========
CoreAGent
=========
@file_name: openai_client.py
@author: Netmind.AI BlackSheep team 
@date: 2024-1-10 
To define the BlackSheep-Agent(The BasicCLass of Agent)
"""


__all__ = ["OpenAIClient"]

import os
import time
import traceback
from typing import Generator, List

from dotenv import load_dotenv
from openai import OpenAI
from openai import Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk


class OpenAIClient:
    """
    The OpenAI client which uses the OpenAI API to generate responses to messages.

    Examples
    --------
    >>> client = OpenAIClient()
    >>> response = client.run([{"role":"user","conten":"Hello, how are you?"}])
    >>> print(response.choices[0].message.content)
    """
    client: OpenAI
    generate_args: dict
    last_time_price: float

    def __init__(self, api_key=None, **generate_args):
        """Initializes the OpenAI Client.

        Parameters
        ----------
        api_key : str, optional
            The OpenAI API key.
        """

        try:
            if api_key is None:
                load_dotenv()
                api_key = os.getenv('OPENAI_API_KEY')
            self.client = OpenAI(api_key=api_key)
        except:
            raise ValueError("The OpenAI client is not available. Please check the OpenAI API key.")

        # Set the default generate arguments for OpenAI's chat completions
        self.generate_args = {
            "model": "gpt-4-0125-preview",
            "temperature": 0.,
            "top_p": 1.0
        }
        # If the user provides generate arguments, update the default values
        self.generate_args.update(generate_args)

    def run(self, messages: List, tools: List = None) -> ChatCompletion | Stream[ChatCompletionChunk]:
        """
        Run the assistant with the given messages.

        Parameters
        ----------
        messages : list
            A list of messages to be processed by the assistant.
        tools : list, optional
            A list of tools to be used by the assistant, by default [].

        Returns
        -------
        str
            The assistant's response to the messages.

        Raises
        ------
        Exception
            If there is an error while processing the messages.
        """

        # If the user provides tools, use them; otherwise, this client will not use any tools
        if tools:
            tool_choice = "auto"
            local_tools = tools
            tools = None    # Reset the tools parameter to avoid errors
        else:
            local_tools = []
            tool_choice = "none"

        get_response_signal = False
        count = 0
        while not get_response_signal and count < 10:
            try:
                # In OpenAI's api, if we request with tools == [], it will make an error. Caz the OpenAI use the default
                # value is 'NOT_GIVEN' which is a special type designed by them.
                if tool_choice == "auto":
                    response = self.client.chat.completions.create(
                        messages=messages,
                        tools=local_tools,
                        tool_choice="auto",
                        **self.generate_args
                    )
                else:
                    response = self.client.chat.completions.create(
                        messages=messages,
                        **self.generate_args
                    )
                get_response_signal = True

                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                self.last_time_price = self.get_oai_fees(self.generate_args['model'], prompt_tokens, completion_tokens)
                return response
            except Exception:
                count += 1
                error_message = str(traceback.format_exc())
                print(f"The error: {error_message}")
                print(f"The messages: {messages}")
                time.sleep(2)

    def stream_run(self, messages: List) -> Generator[str, None, None]:
        """
        Run the assistant with the given messages in a streaming manner.

        Parameters
        ----------
        messages : list
            A list of messages to be processed by the assistant.

        Yields
        ------
        str
            The assistant's response to the messages, yielded one piece at a time.

        Raises
        ------
        Exception
            If there is an error while processing the messages.
        """

        get_response_signal = False
        count = 0
        while not get_response_signal and count < 10:
            try:
                for response in self.client.chat.completions.create(
                        messages=messages,
                        stream=True,
                        timeout=5,
                        **self.generate_args
                ):
                    if response.choices[0].delta.content is None:
                        return None
                    else:
                        text = response.choices[0].delta.content
                        yield text
            except Exception:
                count += 1
                error_message = str(traceback.format_exc())
                print(f"The error: {error_message}")
                print(f"The messages: {messages}")
                time.sleep(2)

    @staticmethod
    def check_generate_args(generate_args: dict) -> None:
        """
        Check the generate arguments.

        Parameters
        ----------
        generate_args : dict
            The generate arguments to be checked.
        """

        assert "llm" in generate_args

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
            "gpt-4-turbo": {
                "prompt": 0.01,
                "completion": 0.03
            },
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
            "gpt-3.5-turbo-instruct": {
                "prompt": 0.0015,
                "completion": 0.002
            },
            "gpt-3.5-turbo-0125": {
                "prompt": 0.0005,
                "completion": 0.0015
            }
        }

        if model_name in openai_price:
            pass
        else:
            raise ValueError(f"Unknown model name {model_name}")

        fee = (openai_price[model_name]["prompt"] * prompt_tokens + openai_price[model_name][
            "completion"] * completion_tokens) / 1000

        return fee
