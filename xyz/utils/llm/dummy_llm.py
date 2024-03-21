"""
=========
CoreAGent
=========
@file_name: core_agent.py
@author: Netmind.AI BlackSheep team
@date: 2024-1-10
To define the BlackSheep-Agent(The BasicCLass of Agent)
"""


from typing import Generator, overload


class DummyLLM:

    def run(self, messages: list, tools=[]) -> str:

        raise TypeError("You do not set a llm-agent in this progress. Please ser a llm-agent first.")

        return None

    def stream_run(self, messages: list) -> Generator[str, None, None]:

        raise TypeError("You do not set a llm-agent in this progress. Please ser a llm-agent first.")

        yield None

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

dummy_agent = DummyLLM()