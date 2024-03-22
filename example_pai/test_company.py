"""
test_company.py
"""

import os

API_KEY = "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"
os.environ["OPENAI_API_KEY"] = API_KEY

from example_pai.interface.pai_company import PaiCompany

if __name__ == "__main__":
    company = PaiCompany()
    print(company)

    question = ("As n ranges over all positive integers，how many possible values can $\operatorname{gcd}(6 n+ 15,10 "
                "n+21)$ equal？The notation $\operatorname{gcd}(a, b)$ represents the greatest common divisor of $a$ "
                "and $b$")

    info = company(question=question)

