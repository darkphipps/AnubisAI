import textwrap
from anpu_storage import OntologyStorage
import openai
import os
from dotenv import load_dotenv
from anpu_utils import get_persona

# Load environment variables from a .env file
load_dotenv()

# Authenticate with OpenAI using the API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Set OpenAI model and parameters
model_engine = "text-davinci-002"
max_tokens = 256

# Connect to or create the ontology database
ontology_storage = OntologyStorage()

def get_persona_description(persona_name):
    return get_persona(persona_name)

def chat(persona_name, user_input):
    persona = get_persona_description(persona_name)
    prompt = f"{persona}\nUser: {user_input}\nAnubis:"
    response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=max_tokens, temperature=0.5)
    answer = response.choices[0].text
    return answer