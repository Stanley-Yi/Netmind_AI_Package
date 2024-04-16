"""
==================
RankPrompts
==================
@file_name: rank_prompts.py
@author: Tianlei Shi
@date: 2024-4-15
"""


__all__ = ["RankPrompts"]

from prettytable import PrettyTable
import openai
from tqdm import tqdm
import itertools
from tenacity import retry, stop_after_attempt, wait_exponential

from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent
from xyz.utils.llm.openai_client import OpenAIClient


class RankPrompts(Agent):
    information: str
    llm_prompt_engineer: LLMAgent

    def __init__(self, core_agent: list[OpenAIClient] | OpenAIClient) -> None:
        """
        The GPTPromptEngineer is a class to generate an optimal prompt for a given task.

        Parameters
        ----------
        core_agent: OpenAIClient
            The core agent of the GPTPromptEngineer.

        Examples
        --------
        >>> from xyz.utils.llm.openai_client import OpenAIClient
        >>> from xyz.function.gpt_prompt_engineer import GPTPromptEngineer
        >>> core_agent = OpenAIClient()
        >>> gpt_prompt_engineer = GPTPromptEngineer(core_agent)
        >>> task = "Build a new prompt from solving k-12 math."
        >>> result = gpt_prompt_engineer(task=task)

        """
        super().__init__()

        # Set the information of the assistant. The information is used to help the user understand the assistant.
        self.set_information({
            "type": "function",
            "function": {
                "name": "GPTPromptEngineer",
                "description": "Generate an optimal prompt for a given task.",
                "parameters": {"task": {"type": "str", "description": "The task which the user want to do."}
                               },
                "required": ["task"],
            },
        })
        self.output_type = "str"

        # Using the template we designed to define the assistant, which can do the main task.
        self.llm_generate_prompt = LLMAgent(template=generate_prompt_engineer, llm_client=core_agent, stream=False)
    
    
    def generate_candidate_prompts(description, test_cases, number_of_prompts):
        outputs = openai.ChatCompletion.create(
            model=CANDIDATE_MODEL, # change this to gpt-3.5-turbo if you don't have GPT-4 access
            messages=[
                {"role": "system", "content": system_gen_system_prompt},
                {"role": "user", "content": f"Here are some test cases:`{test_cases}`\n\nHere is the description of the use-case: `{description.strip()}`\n\nRespond with your prompt, and nothing else. Be creative."}
                ],
            temperature=CANDIDATE_MODEL_TEMPERATURE,
            n=number_of_prompts,
            headers=HEADERS)

        prompts = []

        for i in outputs.choices:
            prompts.append(i.message.content)
        return prompts
    
    
    def expected_score(self, r1, r2):
        return 1 / (1 + 10**((r2 - r1) / 400))

    def update_elo(self, r1, r2, score1):
        e1 = self.expected_score(r1, r2)
        e2 = self.expected_score(r2, r1)
        return r1 + K * (score1 - e1), r2 + K * ((1 - score1) - e2)
    
    
    # Get Score - retry up to N_RETRIES times, waiting exponentially between retries.
    @retry(stop=stop_after_attempt(N_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=70))
    def get_score(description, test_case, pos1, pos2, ranking_model_name, ranking_model_temperature):    
        score = openai.ChatCompletion.create(
            model=ranking_model_name,
            messages=[
                {"role": "system", "content": ranking_system_prompt},
                {"role": "user", "content": f"""Task: {description.strip()}
    Prompt: {test_case['prompt']}
    Generation A: {pos1}
    Generation B: {pos2}"""}
            ],
            logit_bias={
                '32': 100,  # 'A' token
                '33': 100,  # 'B' token
            },
            max_tokens=1,
            temperature=ranking_model_temperature,
            headers=HEADERS,
        ).choices[0].message.content
        return score
    
    
    @retry(stop=stop_after_attempt(N_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=70))
    def get_generation(prompt, test_case):
        generation = openai.ChatCompletion.create(
            model=GENERATION_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"{test_case['prompt']}"}
            ],
            max_tokens=GENERATION_MODEL_MAX_TOKENS,
            temperature=GENERATION_MODEL_TEMPERATURE,
            headers=HEADERS,
        ).choices[0].message.content
        return generation
    
    
    def test_candidate_prompts(self, test_cases, description, prompts):
        # Initialize each prompt with an ELO rating of 1200
        prompt_ratings = {prompt: 1200 for prompt in prompts}

        # Calculate total rounds for progress bar
        total_rounds = len(test_cases) * len(prompts) * (len(prompts) - 1) // 2

        # Initialize progress bar
        pbar = tqdm(total=total_rounds, ncols=70)

        # For each pair of prompts
        for prompt1, prompt2 in itertools.combinations(prompts, 2):
            # For each test case
            for test_case in test_cases:
                # Update progress bar
                pbar.update()

                # Generate outputs for each prompt
                generation1 = self.get_generation(prompt1, test_case)
                generation2 = self.get_generation(prompt2, test_case)

                # Rank the outputs
                score1 = self.get_score(description, test_case, generation1, generation2, RANKING_MODEL, RANKING_MODEL_TEMPERATURE)
                score2 = self.get_score(description, test_case, generation2, generation1, RANKING_MODEL, RANKING_MODEL_TEMPERATURE)

                # Convert scores to numeric values
                score1 = 1 if score1 == 'A' else 0 if score1 == 'B' else 0.5
                score2 = 1 if score2 == 'B' else 0 if score2 == 'A' else 0.5

                # Average the scores
                score = (score1 + score2) / 2

                # Update ELO ratings
                r1, r2 = prompt_ratings[prompt1], prompt_ratings[prompt2]
                r1, r2 = self.update_elo(r1, r2, score)
                prompt_ratings[prompt1], prompt_ratings[prompt2] = r1, r2

                # Print the winner of this round
                if score > 0.5:
                    print(f"Winner: {prompt1}")
                elif score < 0.5:
                    print(f"Winner: {prompt2}")
                else:
                    print("Draw")

        # Close progress bar
        pbar.close()

        return prompt_ratings
    

    def flowing(self, description, test_cases, prompts) -> str:
        """
        The main function of the GPTPromptEngineer.

        Parameters
        ----------
        task: str
            The task which the user want to do.

        Returns
        -------
        str
            The prompts of the GPTPromptEngineer.
        """
        
        prompt_ratings = self.test_candidate_prompts(test_cases, description, prompts)

        # Print the final ELO ratingsz
        table = PrettyTable()
        table.field_names = ["Prompt", "Rating"]
        for prompt, rating in sorted(prompt_ratings.items(), key=lambda item: item[1], reverse=True):
            table.add_row([prompt, rating])

        print(table)

        return prompts




ranking_prompt = [
    {"role": "system", "content": """Your job is to rank the quality of two outputs generated by different prompts. The prompts are used to generate a response for a given task.

You will be provided with the task description, the test prompt, and two generations - one for each system prompt.

Rank the generations in order of quality. If Generation A is better, respond with 'A'. If Generation B is better, respond with 'B'.

Remember, to be considered 'better', a generation must not just be good, it must be noticeably superior to the other.

Also, keep in mind that you are a very harsh critic. Only rank a generation as better if it truly impresses you more than the other.

Respond with your ranking, and nothing else. Be fair and unbiased in your judgement.
"""
    }
]