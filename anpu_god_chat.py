import textwrap
from anpu_storage import OntologyStorage
import openai
import os
from dotenv import load_dotenv
from anpu_utils import get_persona

from anpu_anubis_chat import chat_with_anubis
from anpu_storage import OntologyStorage
from anpu_utils import hybridize_response, get_persona

# Load environment variables from a .env file
load_dotenv()

# Authenticate with OpenAI using the API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Set OpenAI model and parameters
model_engine = "text-davinci-002"
max_tokens = 64

# Connect to or create the ontology database
ontology_storage = OntologyStorage()


def get_persona_description(persona_name):
    persona = get_persona(persona_name)
    return persona if persona else None



ontology_storage = OntologyStorage()

def chat(persona_name, user_input):
    # Get Anubis's response to the user input
    anubis_response = chat_with_anubis(input_text=user_input)

    # Get the persona description for the given name
    persona_desc = get_persona_description(persona_name)

    # Combine the Anubis response and the persona description
    combined_response = f"{persona_desc}\n\n{anubis_response}"

    # Hybridize the response using the combined prompt and user input
    response_text = hybridize_response(combined_response, persona_name, user_input)

    # Store the input and response in the ontology database
    ontology_storage.add_conversation(user_input, response_text)

    # Return the response text
    return response_text



