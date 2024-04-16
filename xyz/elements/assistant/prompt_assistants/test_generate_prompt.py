from xyz.elements.assistant.prompt_assistants.rank_prompts import RankPrompts
from xyz.elements.assistant.prompt_assistants.gpt_prompt_engineer import GPTPromptEngineer
from xyz.utils.llm.openai_client import OpenAIClient
import os
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(
    path.dirname(path.dirname(path.abspath(__file__)))))))


# K is a constant factor that determines how much ratings change
K = 32

CANDIDATE_MODEL_TEMPERATURE = 0.9

GENERATION_MODEL_TEMPERATURE = 0.8
GENERATION_MODEL_MAX_TOKENS = 60

N_RETRIES = 3  # number of times to retry a call to the ranking model if it fails
RANKING_MODEL_TEMPERATURE = 0.5

NUMBER_OF_PROMPTS = 5  # this determines how many candidate prompts to generate... the higher, the more expensive, but the better the results will be

HEADERS = {}


# test_cases
# this style of description tends to work well
description = "Given a prompt, generate a landing page headline."

test_cases = [
    {
        'prompt': 'Promoting an innovative new fitness app, Smartly',
    },
    {
        'prompt': 'Why a vegan diet is beneficial for your health',
    },
    {
        'prompt': 'Introducing a new online course on digital marketing',
    },
    {
        'prompt': 'Launching a new line of eco-friendly clothing',
    },
    {
        'prompt': 'Promoting a new travel blog focusing on budget travel',
    },
    {
        'prompt': 'Advertising a new software for efficient project management',
    },
    {
        'prompt': 'Introducing a new book on mastering Python programming',
    },
    {
        'prompt': 'Promoting a new online platform for learning languages',
    },
    {
        'prompt': 'Advertising a new service for personalized meal plans',
    },
    {
        'prompt': 'Launching a new app for mental health and mindfulness',
    }
]


API_KEY = "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"

prompt_agent = OpenAIClient(
    api_key=API_KEY, temperature=CANDIDATE_MODEL_TEMPERATURE, n=NUMBER_OF_PROMPTS)
engineer = GPTPromptEngineer(prompt_agent)

prompts = engineer.flowing(test_cases, description)
print(prompts)


generation_agent = OpenAIClient(api_key=API_KEY, max_tokens=GENERATION_MODEL_MAX_TOKENS, temperature=GENERATION_MODEL_TEMPERATURE)
score_agent = OpenAIClient(api_key=API_KEY, max_tokens=1, temperature=GENERATION_MODEL_TEMPERATURE, logit_bias={
        '32': 100,  # 'A' token
        '33': 100,  # 'B' token
    })


