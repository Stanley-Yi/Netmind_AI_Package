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
    
    N_RETRIES = 3  # number of times to retry a call to the ranking model if it fails

    def __init__(self, generation_agent: OpenAIClient, score_agent: OpenAIClient, k: int) -> None:
        """
        The RankPrompts is a class to rank a list of prompts based on their performance.

        Parameters
        ----------
        generation_agent: OpenAIClient
            The agent to generate result according to specific prompt.
        score_agent: OpenAIClient
            The agent to score the performance of prompt's result.
        k: int
            A constant factor that determines how much ratings change.

        Examples
        --------
        >>> from xyz.utils.llm.openai_client import OpenAIClient
        >>> from xyz.function.rank_prompts import RankPrompts
        >>> generation_agent = OpenAIClient()
        >>> score_agent = OpenAIClient()
        >>> k = 32
        >>> gpt_prompt_engineer = GPTPromptEngineer(generation_agent, score_agent, k)
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
                "parameters": {"test_cases": {"type": "list", "test_cases": "Some examples of the task."},
                               "description": {"type": "str", "description": "Description of the task which the user want to do."},
                               "prompts": {"type": "list", "prompts": "Prompts that need to be compared."}
                               },
                "required": ["test_cases", "description", "prompts"],
            },
        })
        self.output_type = "str"

        # Using the template we designed to define the assistant, which can do the main task.
        self.llm_generation_agent = LLMAgent(template=generation_prompt, llm_client=generation_agent, stream=False)
        self.llm_score_agent = LLMAgent(template=ranking_prompt, llm_client=score_agent, stream=False)
        
        self.K = k
    
    
    def expected_score(self, r1, r2):
        return 1 / (1 + 10**((r2 - r1) / 400))
    

    def update_elo(self, r1, r2, score1):
        e1 = self.expected_score(r1, r2)
        e2 = self.expected_score(r2, r1)
        return r1 + self.K * (score1 - e1), r2 + self.K * ((1 - score1) - e2)
    
    
    # Get Score - retry up to N_RETRIES times, waiting exponentially between retries.
    @retry(stop=stop_after_attempt(N_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=70))
    def get_score(self, description, test_case, pos1, pos2):    
        
        return self.llm_score_agent(description=description.strip(), test_case=test_case, pos1=pos1, pos2=pos2)
    
    
    @retry(stop=stop_after_attempt(N_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=70))
    def get_generation(self, prompt, test_case):

        return self.llm_generation_agent(prompt=prompt, test_case=test_case['task'])
    
    
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
                score1 = self.get_score(description, test_case, generation1, generation2)
                score2 = self.get_score(description, test_case, generation2, generation1)

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
    

    def flowing(self, test_cases, description, prompts) -> str:
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

        return table



ranking_prompt = [
    {"role": "system", "content": """Your job is to rank the quality of two outputs generated by different prompts. The prompts are used to generate a response for a given task.

You will be provided with the task description, the test task (may include expectation output), and two generations - one for each system prompt.

Rank the generations in order of quality (check which generation is closer to the expectation if expectation provided). If Generation A is better, respond with 'A'. If Generation B is better, respond with 'B'.

Remember, to be considered 'better', a generation must not just be good, it must be noticeably superior to the other.

Also, keep in mind that you are a very harsh critic. Only rank a generation as better if it truly impresses you more than the other.

Respond with your ranking, and nothing else. Be fair and unbiased in your judgement.
"""
    },
    {"role": "user", "content": """Task: {description}
        Prompt: {test_case}
        Generation A: {pos1}
        Generation B: {pos2}"""}
]


generation_prompt = [
    {"role": "system", "content": """{prompt}"""},
    {"role": "user", "content": "{test_case}"}
]