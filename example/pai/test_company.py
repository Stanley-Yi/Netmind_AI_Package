"""
test_company.py
"""

import os
import sys 
sys.path.append("../..")

API_KEY = "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"
os.environ["OPENAI_API_KEY"] = API_KEY


from interface.pai_company import PaiCompany

if __name__ == "__main__":
    company = PaiCompany()
    print(company)

    question = ("As n ranges over all positive integers，how many possible values can $\operatorname{gcd}(6 n+ 15,10 "
                "n+21)$ equal？The notation $\operatorname{gcd}(a, b)$ represents the greatest common divisor of $a$ "
                "and $b$")

    info = company(question=question)

