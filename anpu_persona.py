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

def get_persona(name="Morgan", god="Anubis"):
    # Get the current persona for the specified god from the ontology database
    persona = ontology_storage.get_similar_responses(f"{god} persona")

    # If the persona is not found in the ontology database, generate a new persona using OpenAI
    if persona is None:
        # Set OpenAI prompt to generate a new persona for the specified god
        prompt = f"Generate a new {god} persona for {name}:\n{god}: "

        response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=max_tokens)

        # Set the new persona based on the OpenAI response
        persona = response.choices[0].text.strip()
        persona = persona.replace("god of death and the afterlife", "god of the afterlife")

        # Store the new persona in the ontology database
        ontology_storage.add_ontology(f"{god} persona", persona)

    # Return the persona
    return persona

