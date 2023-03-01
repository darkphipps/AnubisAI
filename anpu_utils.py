import textwrap
from anpu_storage import OntologyStorage
import openai
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Authenticate with OpenAI using the API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Set OpenAI model and parameters
model_engine = "text-davinci-002"
max_tokens = 256

# Connect to or create the ontology database
ontology_storage = OntologyStorage()

def get_persona(persona_name):
    if persona_name == "Anubis":
        return "Hello, I am Anubis. I am an AI designed to help you with your tasks."
    persona = ontology_storage.get_similar_responses(f"{persona_name} persona")
    if persona is None:
        prompt = f"Generate a new persona for {persona_name}:\n"
        response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=max_tokens, temperature=0.5)
        persona = response.choices[0].text.strip()
        persona = textwrap.shorten(persona, width=64, placeholder='...')
        ontology_storage.add_ontology(f"{persona_name} persona", persona)
    return persona