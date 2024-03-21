import sys 
sys.path.append("../..")

import os 
# 请在这里 补充上 API-Key
API_KEY = "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"
os.environ["OPENAI_API_KEY"] = API_KEY 

from xyz.utils.api_wrap_tool import APIWrapTool

def add_method(a,b):
    return a+b 

add_method_doc = "我们可以传进来两个数字，然后会返回这两个数字之和。"

import threading 

add_api = APIWrapTool(add_method, add_method_doc)

t_1 = threading.Thread(target=add_api.run_api)
t_1.start()

