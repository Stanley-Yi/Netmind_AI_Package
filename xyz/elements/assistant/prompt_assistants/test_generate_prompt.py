import os
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(
    path.dirname(path.dirname(path.abspath(__file__)))))))

from xyz.elements.assistant.prompt_assistants.rank_prompts import RankPrompts
from xyz.elements.assistant.prompt_assistants.gpt_prompt_engineer import GPTPromptEngineer
from xyz.utils.llm.openai_client import OpenAIClient


# K is a constant factor that determines how much ratings change
K = 32

CANDIDATE_MODEL_TEMPERATURE = 0.9

GENERATION_MODEL_TEMPERATURE = 0.8
GENERATION_MODEL_MAX_TOKENS = 200

RANKING_MODEL = 'gpt-4-turbo'
RANKING_MODEL_TEMPERATURE = 0.5

NUMBER_OF_PROMPTS = 2  # this determines how many candidate prompts to generate... the higher, the more expensive, but the better the results will be


# test_cases
# this style of description tends to work well
# description = "Given a prompt, generate a landing page headline."

# test_cases = [
#     {
#         'prompt': 'Promoting an innovative new fitness app, Smartly',
#     },
#     {
#         'prompt': 'Why a vegan diet is beneficial for your health',
#     },
#     {
#         'prompt': 'Introducing a new online course on digital marketing',
#     },
#     {
#         'prompt': 'Launching a new line of eco-friendly clothing',
#     },
#     {
#         'prompt': 'Promoting a new travel blog focusing on budget travel',
#     },
#     {
#         'prompt': 'Advertising a new software for efficient project management',
#     },
#     {
#         'prompt': 'Introducing a new book on mastering Python programming',
#     },
#     {
#         'prompt': 'Promoting a new online platform for learning languages',
#     },
#     {
#         'prompt': 'Advertising a new service for personalized meal plans',
#     },
#     {
#         'prompt': 'Launching a new app for mental health and mindfulness',
#     }
# ]

description = "Given a question, please solve this question and generate a detailed solution for the question."

test_cases = [
    {
        'task': 'How many different real numbers $$x$$ satisfy the equation $$\left(x^{2}-5\right)^{2}=16 ?$$ ( )',
        'exception': ' Correct answer: 4'
    },
    {
        'task': 'What is the area of the triangle formed by the lines $$y=5$$，$$y=1+x$$，and $$y=1-x$$？( )',
        'exception': ' Correct answer: 16'
    },
    {
        'task': 'Alice has $$24$$ apples．In how many ways can she share them with Becky and Chris so that each of the three people has at least two apples？( )',
        'exception': ' Correct answer: 190'
    },
    {
        'task': 'At the 2013 Winnebago County Fair a vendor is offering a ``fair special" on sandals．If you buy one pair of sandals at the regular price of $$\$ 50 $$, you get a second pair at a $$ 40\% $$ discount, and a third pair at half the regular price. Javier took advantage of the "fair special" to buy three pairs of sandals. What percentage of the \$ $$150$$ regular price did he save？( )',
        'exception': ' Correct answer: 30'
    },
    {
        'task': 'Ralph went to the store and bought 12 pairs of socks for a total of $$\$ 24 $$. Some of the socks he bought cost \$ $$ 1$$ a pair，some of the socks he bought cost $$\$ 3 $$ a pair, and some of the socks he bought cost \$ $$ 4$$ a pair．If he bought at least one pair of each type，how many pairs of $$\$ 1 $$ socks did Ralph buy？( )',
        'exception': ' Correct answer: 7'
    },
]


API_KEY = "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"

prompt_agent = OpenAIClient(
    api_key=API_KEY, temperature=CANDIDATE_MODEL_TEMPERATURE, n=NUMBER_OF_PROMPTS)
engineer = GPTPromptEngineer(prompt_agent)

prompts = engineer.flowing(test_cases, description)
print(prompts)


generation_agent = OpenAIClient(api_key=API_KEY, model=RANKING_MODEL, max_tokens=GENERATION_MODEL_MAX_TOKENS, temperature=GENERATION_MODEL_TEMPERATURE)
score_agent = OpenAIClient(api_key=API_KEY, model=RANKING_MODEL, max_tokens=1, temperature=GENERATION_MODEL_TEMPERATURE, logit_bias={
        '32': 100,  # 'A' token
        '33': 100,  # 'B' token
    })

ranker = RankPrompts(generation_agent, score_agent, K)
comparison = ranker.flowing(test_cases, description, prompts)
print(comparison)

print("\nWinner: \n")
print(comparison._rows[0][0])