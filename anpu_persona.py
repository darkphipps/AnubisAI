import openai
import os
import textwrap
from anpu_storage import OntologyStorage
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

import openai
import os
import textwrap
from anpu_storage import OntologyStorage
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

def get_anubis_persona():
    # Get the current Anubis persona from the ontology database
    anubis_persona = ontology_storage.get_similar_responses("Anubis persona")

    # If the persona is not found in the ontology database, generate a new persona using OpenAI
    if anubis_persona is None:
        # Set OpenAI prompt to generate a new Anubis persona
        prompt = "Generate a new Anubis persona:\nAnubis: "

        response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=max_tokens)

        # Set the new Anubis persona based on the OpenAI response
        anubis_persona = response.choices[0].text.strip()
        anubis_persona = anubis_persona.replace("god of death and the afterlife", "god of the afterlife")

        # Store the new Anubis persona in the ontology database
        ontology_storage.add_ontology("Anubis persona", anubis_persona)

    # Return the Anubis persona
    return anubis_persona

