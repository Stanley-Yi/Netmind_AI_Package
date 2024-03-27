"""
==============
MathVerifierCodeGenerator
==============
@file_name: math_verifier_code_generator
@author: He Yan
@date: 2024-3-25
"""

from xyz.node.agent import Agent
from xyz.node.basic.llm_agent import LLMAgent

from ..global_parameters import openai_client
from textwrap import dedent

class MathVerifierCodeGenerator(Agent):
    def __init__(self) -> None:
        super().__init__(openai_client)
        
        # 1. Set Agent attributes for building society in XYZ later version
        # For example, description might be used to show the agent's function 
        # in the society and guide a manager agent to choose the right agent.
        self.set_name("MathVerifierCodeGenerator")
        self.set_description("This is a Python programming and math teacher, who can verify the answer of a math problem by implementing a Python function named `solution`.")
        self.set_parameters({
                "problem": {
                    "type": "str",
                    "description": "The math problem need to be verified."
                },
                "answer": {
                    "type": "str",
                    "description": "The answer need to be verified."
                }
            })
        
        # 2. Initialize sub-agents for your custom agent
        # In your custom agent, you may integrate multiple other agents to achieve the goal.
        # LLMAgent is a built-in agent in XYZ, which can be used to interact with OpenAI API.
        self.llm_code_verifier = LLMAgent(template=MATHANSWER_VERIFIER_TEMPLATE, 
                                        core_agent=openai_client, 
                                        inner_multi=False, 
                                        stream=False)
    
    def flowing(self, problem: str, answer: str) -> str:
        code = self.llm_code_verifier(problem=problem, answer=answer)
        # remove the code block
        if code.startswith("```python3"):
            code = code.replace("```python3", "").rstrip("```")
        elif code.startswith("```python"):
            code = code.replace("```python", "").rstrip("```")
        elif code.startswith("```"):
            code = code.lstrip("```").rstrip("```")
        return code

MATHANSWER_VERIFIER_TEMPLATE = {
    "system": dedent("""As a Python programming and math teacher, I will give you a math question and an answer. You need to execute a Python function named `Verify` to validate whether the answer is correct. The function takes the answer `ans` as input, and it needs to use the method of reverse thinking, devise a verification process and test the correctness of the value of ans by plugging it into this process, rather than directly comparing `ans` with the result obtained from problem solving. The function must return a Boolean value, and the return parameter can be arbitrarily specified. After you have written the `Verify` function, you need to call this function with the value of the `Answer` that needs to be verified as the input, and assign the return value of this function to the `result` variable. Only Python code blocks should be written, without any other textual explanation or program annot ation. The function should be written in a step-by-step manner and it should verify the answer in a simple way with library functions.

        Here are three examples how to do it:

        # Question: What is the remainder when $${{{{2}}^{{10}}}}$$ is divided by $$3$$?
        # Answer: 2
        # Python Code:
        ```
        def Verify(ans):
            power = 2 ** 10
            sub = power - ans
            if sub % 3 == 0:
            return True
            else: 
            return False
        result = Verify(2)
        ```

        # Question: Lucy, Peter, Edmund and Susan shared £$120$.  Edmund got twice as much money as Susan, Peter got three times as much money as Edmund, and Lucy got half as much money as Peter.  How much money did Lucy get?
        # Answer: 30
        # Python Code:
        ```
        def Verify(ans): 

            lucy = ans
            peter = 2 * ans
            edmund = 2 * ans / 3
            susan = ans / 3
            total = lucy + peter + edmund + susan
            if total == 120:
            istrue = True
            else:
            istrue = False
            return istrue
        result = Verify(30)
        ```

        # Question: How many terms are there in the sequence below?  $2, 4, 6, 8,10 \\dots ~240$.
        # Answer: 120
        # Python Code: 
        ```
        def Verify(ans):
            first_term = 2
            last_term = 240
            common_difference = 2
            num_terms = ans
            if  (first_term + (num_terms - 1) * common_difference) == 240:
                return True
            else:
                return False
        result = Verify(120)
        ```

        And here is a wrong case:
        # Question: Two buildings are $$90\\textasciitilde\\text{{m}}$$ apart from each other. $$9$$ trees are planted at regular intervals between the two buildings. What is the distance between each tree?
        # Answer: 9
        # Python Code:
        ```
        def Verify(ans):
            total_distance = 90
            total_trees = 9
            distance = total_distance / (total_trees + 1)
            if distance == ans:
                return True
            else:
                return False
        result = Verify(9)

        In the above wrong case, the function directly calculate the value of `distance`, which is the answer to the problem, and compare it with `ans`. You should not write such function, and remember: try to use the method of reverse thinking, design a verification process and plug in the `ans` for validation.


        Please follow the instructions below:
        - You will only write in code blocks and not output any other textual explanation or program annotation
        - You can use any variable name you want, but final function name has to be `Verify`, and the input of the function has to be `ans`
        - You can import any library you need, like `math` and so on
        - Do not directly compare `ans` with your answer in the format 'ans == `your answer`'
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
        # Answer: {answer}
        # Python Code:
        ```
        """)
}