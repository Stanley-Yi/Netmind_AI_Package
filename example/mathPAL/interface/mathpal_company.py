from ..agents.math_code_generator import MathCodeGenerator
from ..agents.math_code_interpreter import MathCodeInterpreter
from ..agents.math_verifier_code_generator import MathVerifierCodeGenerator
from ..agents.verify_and_vote import VerifyAndVote
from xyz.node.agent import Agent
from global_parameters import logger

class MathPALCompany(Agent):
    def __init__(self) -> None:
        super().__init__()
        
        # 1. Set Agent attributes for building society in XYZ later version
        # For example, description might be used to show the agent's function 
        # in the society and guide a manager agent to choose the right agent.
        self.set_name("MathPALCompany")
        self.set_description("This is a company that uses Python programming and math to solve math problems and return a numerical answer.")
        self.set_parameters({
                "problem": {
                    "type": "str",
                    "description": "The math problem need to be solved."
                },
                "solution_number": {
                    "type": "str",
                    "description": "The number of solutions to try when solving the problem."
                }
            })
        
        # 2. Initialize sub-agents for your custom agent
        # In your custom agent, you may integrate multiple other agents to achieve the goal.
        self.math_code_generator = MathCodeGenerator()
        self.math_code_interpreter = MathCodeInterpreter()
        self.math_verifier_code_generator = MathVerifierCodeGenerator()
        self.verify_and_vote = VerifyAndVote()
    
    def flowing(self, problem: str, solution_number: int) -> str:
        # Step 1. Generate multiple solutions to the problem
        answers = []
        for i in range(solution_number):
            solution_code = self.math_code_generator(problem=problem)
            logger.info (f"Generate {i+1} solution code")
            # save code for debug
            with open(f"./solu_{i}.py", "w") as f:
                f.write(solution_code)

            try:
                answer = self.math_code_interpreter(code=solution_code)
                answers.append(answer)
                logger.info (f"Solution {i+1} Code execution success, answer: {answer}")
            except Exception as e:
                logger.info (f"Solution {i+1} Code execution failed {e}")
        if len(answers) == 0:
            return "No answer found."
        # Step 2. Generate a verification code for the answer
        # We only need to generate one verification code for the first answer, 
        # because the verification code is the same for all answers.
        verification_code = self.math_verifier_code_generator(problem=problem, answer=answers[0])
        logger.info(f"Generate verification code")

        # save code for debug
        with open("./tmp.py", "w") as f:
            f.write(verification_code)

        # Step 3. Verify the answer
        return self.verify_and_vote(answers=answers, code=verification_code)
