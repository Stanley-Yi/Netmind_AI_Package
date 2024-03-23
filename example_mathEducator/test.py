import os

API_KEY = ""
os.environ["OPENAI_API_KEY"] = API_KEY


from example_mathEducator.agents.cot import Cot 


if __name__ == "__main__":
    
    cot_solver = Cot()
    
    question = ("As n ranges over all positive integers，how many possible values can $\operatorname{gcd}(6 n+ 15,10 "
            "n+21)$ equal？The notation $\operatorname{gcd}(a, b)$ represents the greatest common divisor of $a$ "
            "and $b$")

    info = cot_solver(question=question)
    
    for ans in info:
        print(ans, end="")
    
    
    