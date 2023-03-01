import openai
import os
from anpu_storage import MindStorage
from dotenv import load_dotenv
from anpu_god_chat import chat_with_mind

# Load environment variables from a .env file
load_dotenv()

# Authenticate with OpenAI using the API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Set OpenAI model and parameters
model_engine = "text-davinci-002"
max_tokens = 64

# Connect to or create the mind database
mind_storage = MindStorage()

def chat_with_mind(user_input):
    # Use the chat_with_mind function from anpu_god_chat to get a response from Anpu's mind
    response = chat_with_mind(user_input)

    # If no response is found, generate a new one using OpenAI
    if not response:
        prompt = "Generate a response for:\n" + user_input + "\n"
        response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=max_tokens, temperature=0.5)
        response = response.choices[0].text.strip()
        mind_storage.add_response(response)

    return response
