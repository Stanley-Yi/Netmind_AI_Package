from xyz.utils.logger import create_logger
from dotenv import load_dotenv
import os
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
logger = create_logger(f"./logs")
logger.info(f"Using OPENAI_API_KEY: {OPENAI_API_KEY}")

# Init a global OpenAI client with temperature 0.0 to get a deterministic and more accurate response
from xyz.utils.llm.openai_client import OpenAIClient
openai_client = OpenAIClient(api_key=OPENAI_API_KEY, temperature=0.0)