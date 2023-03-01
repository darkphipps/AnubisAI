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
max_tokens = 64

# Connect to or create the ontology database
ontology_storage = OntologyStorage()

def get_persona(persona_name):
    persona = ontology_storage.get_similar_responses(f"{persona_name} persona")
    if persona is None:
        prompt = f"Generate a new persona for {persona_name}:\n"
        response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=max_tokens, temperature=0.5)
        persona = response.choices[0].text.strip()
        persona = textwrap.shorten(persona, width=64, placeholder='...')
        ontology_storage.add_ontology(f"{persona_name} persona", persona)
    return persona

def chat_with_anubis(input_text):
    persona_name = "Anubis"
    persona = get_persona(persona_name)
    chat_history = []
    response = ""

    while not response:
        prompt = f"{input_text}\n\nAnubis: {chat_history[-2:]}\nUser: {input_text}\nAnubis:"
        response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=max_tokens, temperature=0.5)
        response_text = response.choices[0].text.strip()
        if not response_text:
            response = ""
            continue
        chat_history.append(response_text)
        response = f"{persona}{response_text}"
    return response
