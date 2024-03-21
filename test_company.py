import sys
import os
API_KEY = "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"
os.environ["OPENAI_API_KEY"] = API_KEY

from example_pai.interface.pai_company import PaiCompany

company = PaiCompany()
company()