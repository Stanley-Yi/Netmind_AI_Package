""" 
============
ThinkingFlow
============
Using multi-agents to build a thinking-flow to process the complex tasks.
"""


from xyz.magics.agent.CoreAgent import CoreAgent
import time
from copy import deepcopy
import traceback


# 这个class 目前是专门服务于 consciousness & momentum 的
class ThinkingFlow():
    
    def __init__(self, agents_dict):
        self.agents_dict = agents_dict 
    
    def _set_template(self):

        system = self.template["System"]
        user = self.template["Human"]
        
        self.prompts = system + "||--||" + user

    # To Hongyi： 先按咱的老方法去做 Thinking-Flow。用固定的对象方法来表达。
    def run(self, **kwargs):
        """
        Run the thinking-flow to process the complex tasks.
        """
        prefix = self.prompts.format(**kwargs)

        [system, user] = prefix.split("||--||")
        
        if self.messages:
            system += f"\nPlease take a look at your previous user history and do not make same mistakes again."

        local_messages = deepcopy(self.messages)

        message = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        
        local_messages.extend(message)

        get_response_signal = False
        count = 0
        while not get_response_signal and count < 10:
            try:
                response = self.client.chat.completions.create(
                    model=self.llm,
                    messages=local_messages,
                    temperature=self.temperature,
                )
                get_response_signal = True
            except Exception as e:
                count += 1
                error_message = str(traceback.format_exc())
                # print(f"API ERROR: We will sleep in 30s and try again. The max repeat times is 10. This is the {count} time")
                print(f"The error: {error_message}")
                time.sleep(2)

        answer = response.choices[0].message.content
        self.logger.info(f"************|||----|||访问 API 一次|||----|||************\n\n{answer}")
        return answer
        raise NotImplementedError

