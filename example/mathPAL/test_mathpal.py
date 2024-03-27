from example.mathPAL.interface.mathpal_company import MathPALCompany

if __name__ == "__main__":
    
    mathpal_company = MathPALCompany()
    print (mathpal_company)

    problem = ("As n ranges over all positive integers, how many possible values can $\operatorname{gcd}(6 n+ 15,10 "
            "n+21)$ equal? The notation $\operatorname{gcd}(a, b)$ represents the greatest common divisor of $a$ "
            "and $b$")


    answer = mathpal_company(problem=problem, solution_number=5)
    
    print ()
    for s in answer:
        print(s, end="")
    
    