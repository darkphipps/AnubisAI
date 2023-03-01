import textwrap
from anpu_storage import OntologyStorage
import openai
import os
from dotenv import load_dotenv
from anpu_anubis_chat import chat_with_anubis
from anpu_persona import get_persona_description
from anpu_persona import get_persona

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
    if persona is not None and len(persona) > 0:
        return persona[0]
    else:
        if persona_name == "Anubis":
            persona = chat_with_anubis(input_text=persona_name)
        else:
            prompt = f"Generate a new persona for {persona_name}:\n"
            response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=max_tokens, temperature=0.5)
            persona = response.choices[0].text.strip()
            persona = textwrap.shorten(persona, width=64, placeholder='...')

        ontology_storage.add_ontology(f"{persona_name} persona", persona)
        return ontology_storage.get_similar_responses(f"{persona_name} persona")[0]

def get_persona_description(persona_name):
    persona = get_persona(persona_name)
    if isinstance(persona, str):
        return None
    else:
        return persona.description



def hybridize_response(combined_response, persona_name, user_input):
    # Get the persona for the given name
    persona = get_persona_description(persona_name)

    # Combine the combined response and the persona description
    full_response = f"{combined_response}\n{persona}"

    # Store the input and response in the ontology database
    ontology_storage.add_conversation(user_input, full_response)

    # Return the full response
    return full_response
