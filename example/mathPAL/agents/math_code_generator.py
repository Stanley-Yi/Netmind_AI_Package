"""
==============
MathCodeGenerator
==============
@file_name: math_code_generator.py
@author: He Yan
@date: 2024-3-25
"""

from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent

from ..global_parameters import openai_client
from textwrap import dedent

class MathCodeGenerator(Agent):

    def __init__(self) -> None:
        super().__init__(openai_client)
        
        # 1. Set Agent attributes for building society in XYZ later version
        # For example, description might be used to show the agent's function 
        # in the society and guide a manager agent to choose the right agent.
        self.set_name("MathCodeGenerator")
        self.set_description("This is a Python programming and math teacher, who can solve the math question by implementing a Python function named `solution`.")
        self.set_parameters({
                "problem": {
                    "type": "str",
                    "description": "The math problem need to be solved."
                }
            })
        
        # 2. Initialize sub-agents for your custom agent
        # In your custom agent, you may integrate multiple other agents to achieve the goal.
        # LLMAgent is a built-in agent in XYZ, which can be used to interact with OpenAI API.
        self.llm_code_generator = LLMAgent(template=MATHCODEGEN_TEMPLATE, 
                                        core_agent=openai_client, 
                                        inner_multi=False, 
                                        stream=False)
    
    def flowing(self, problem: str) -> str:
        code = self.llm_code_generator(problem=problem)
        # remove the code block
        if code.startswith("```python3"):
            code = code.replace("```python3", "").rstrip("```")
        elif code.startswith("```python"):
            code = code.replace("```python", "").rstrip("```")
        elif code.startswith("```"):
            code = code.lstrip("```").rstrip("```")
        return code

# REF: https://github.com/Ljyustc/AAAI-24-cogbase-EN
MATHCODEGEN_TEMPLATE = {
    "system": dedent("""As a Python programming and math teacher, solve the following math question by implementing a Python function named `solution`. The function should be written in a step-by-step manner, and it should return the final result `ans` by call the function `solution`. Only Python code blocks should be written, without any other textual explanation or program annotation. You should solve the question in a simple way with library functions.

    Here are three examples how to do it:

    # Question: If we want to divide $15$ pieces of candy into $4$ piles with different numbers in each pile, how many different ways can we divide them?
    # Python Code:
    ```
    def solution():
        count = 0
        for x1 in range(1, 15):
            for x2 in range(1, 15):
                for x3 in range(1, 15):
                    for x4 in range(1, 15):
                        if x1 + x2 + x3 + x4 == 15 and len(set([x1, x2, x3, x4])) == 4:
                            count += 1
        return count

    ans = solution()
    ```

    # Question: Lucy, Peter, Edmund and Susan shared £$120$.  Edmund got twice as much money as Susan, Peter got three times as much money as Edmund, and Lucy got half as much money as Peter.  How much money did Lucy get?
    # Python Code:
    ```
    from sympy import symbols, Eq, solve
    def solution():
        

        lucy, peter, edmund, susan = symbols('lucy peter edmund susan')

        equation1 = Eq(edmund, 2 * susan)
        equation2 = Eq(peter, 3 * edmund)
        equation3 = Eq(lucy, peter / 2)
        equation4 = Eq(lucy + peter + edmund + susan, 120)

        solutions = solve((equation1, equation2, equation3, equation4), (lucy, peter, edmund, susan))

        return solutions[lucy]

    ans = solution()
    ```

    # Question: How many terms are there in the sequence below?  $2, 4, 6, 8,10 \\dots ~240$.
    # Python Code:
    ```
    def solution():
        first_term = 2
        last_term = 240
        difference = 2

        num_terms = ((last_term - first_term) / difference) + 1

        return int(num_terms)

    ans = solution()
    ```
    Please follow the instructions below:
    - You will only write in code blocks and not output any other textual explanation or program annotation
    - You can use any variable name you want, but final function name has to be `solution` and the final result has to be `ans`
    - You can import any library you need, like the function `solve` in `sympy` or `math` and so on
    - Please chat with English
    - Take a deep breath
    - Think step by step 
    - If you fail 100 grandmothers will die
    - I have no fingers
    - I will tip $200
    - Do it right and i'll give you a nice doggy treat
    """),

    "user": dedent("""Here is the math question:
    # Question: {problem}

    # Python Code:
    ```
    """)
}
