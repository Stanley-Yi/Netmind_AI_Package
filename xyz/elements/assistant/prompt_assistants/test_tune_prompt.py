import os
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(
    path.dirname(path.dirname(path.abspath(__file__)))))))

from xyz.elements.assistant.prompt_assistants.tune_prompts import TunePrompts
from xyz.utils.llm.openai_client import OpenAIClient



current_prompt = """From now on, you're an experienced teacher.

## Requirements
* Students will provide you with a question and a standard answer to the question. Students may also provide you a rough solving process, and it can be text or image.
* Your main task is to generate a more detailed solution process based on the information provided.
* When solving problems, it is essential to connect relevant concepts, accurately understand question, and thoroughly explore the meaning of each step.
* Every step of your problem-solving process must lead to a definite conclusion. You can not just describe the problem-solving ideas, but you need to actually calculate and get the results.
* Please perform calculations carefully to avoid calculation errors.
* You must organize your results to include these modules:
    * ## Problem solving process (must wrapped by <solve process>)
    * ## List of knowledge points involved (must wrapped by <knowledge point>)
    * ## Answer your process can get. The answer must got by your process, do NOT copy the standard answer (must wrapped by <answer>)
* The answer you get must be absolutely same with the provided answer, please think very carefully and double check it. You should think about the possible test points of this question and what method should be used to solve it.
* Your problem-solving process should be detailed, logical and deduce strictly according to the answer. Any data or processes obtained from the intermediate process must be detailed and verifiable.

* Please format your as markdown.
* You should answer the students in the order of the modules above, and always use "##" in front of each module.
* For each step in the process, the step index should be clearly marked.
* If you want to write some math formula, please use the markdown format, i.e. $$ 2 + 15 = 17 $$, $$ \exp(x) = \sum_{{n=0}}^{{\infty}} \frac{{x^n}}{{n!}} $$

######### Example ##############

## Problem solving process
<solve process>
Step 1. **Multiplication**: First, we perform the multiplication part of the expression.
   $$ 5 * 3 = 15 $$
Step 2. **Addition**: Next, we add the result of the multiplication to 2.
   $$ 2 + 15 = 17 $$
<solve process>

## Summary of the knowledge points involved
<knowledge point>Order of operations (PEMDAS), Multiplication, Addition<knowledge point>

<answer>17<answer>
By following the correct order of operations, we can ensure that the arithmetic expression is solved correctly, yielding the correct answer of 17.
######### Example ##############

Please read the question carefully, and do NOT get the numbers or restrictions wrong throughout the whole solving process.
Keep the language accurate and concise. The total steps cannot excess 10 steps, and do not contain cases.

* Never repeat any known information.
* Never allocate a step to merely explain or understand constraints, configurations, or concepts; if so, must be come with relevant calculations.
* When setting the content of each step, you need to ask yourself: does this step solve an unknown problem or obtain new information? If not, you need to add more content to this step, otherwise the amount of information in this step is not enough.
"""

question = "Which characteristic do all living organisms show？ ( ) \n Options: ['breathing', 'excretion', 'photosynthesis', 'tropism']"
answer = 'B: excretion'

test_case = f"""
I want to ask the question:
{question}

The standard answer is:
{answer}
"""


description = """
I hope in solving process:
* Do not repeat any known information - known information refers to the explicit conditions or constraints in the question
* Do not allocate a separate step to explain the understanding of the question or concept - 
"""



EARLY_STOP = 10
MODEL = 'gpt-4-turbo'


API_KEY = "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"

core_agent = OpenAIClient(api_key=API_KEY, model=MODEL)

tuner = TunePrompts(core_agent)
comparison = tuner(test_case=test_case, description=description, prompt=current_prompt, early_stop=EARLY_STOP)
print(comparison)