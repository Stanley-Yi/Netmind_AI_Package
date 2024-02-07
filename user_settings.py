import os
from openai import OpenAI


# 请在这里 补充上 API-Key
API_KEY = "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"
os.environ["OPENAI_API_KEY"] = API_KEY 

# 可以去直接 import 这个 client
# 例子: 
# from user_settings import client
client = OpenAI(
    api_key = os.environ.get(
        API_KEY),
)

