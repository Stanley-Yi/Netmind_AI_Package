import dotenv
import json
dotenv.load_dotenv()
from openai import OpenAI
client = OpenAI()

tools = [
  {
    "type": "function",
    "function": {
    "name": "PlanAgent",
    "description": "This function can help user to make a plan for solving the question step by step.",
    "parameters": {
        "type": "object",
        "properties": {
        "question": {
            "type": "string",
            "description": "The question here which need help.",
        }
        },
        "required": ["question"],
    },
    }
}
]
messages = [{"role": "user", "content": "How can I solve the 6^237-8^23?"}]
completion = client.chat.completions.create(
  model="gpt-4-turbo",
  messages=messages,
  tools=tools,
  tool_choice="auto"
)

print(completion)

parameters = completion.choices[0].message.tool_calls[0].function.arguments
parameters = json.loads(parameters)
print(parameters)
