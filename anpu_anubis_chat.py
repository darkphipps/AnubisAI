import openai
import os
import textwrap
from anpu_storage import OntologyStorage
from dotenv import load_dotenv
from anpu_persona import get_persona

# Load environment variables from a .env file
load_dotenv()

# Authenticate with OpenAI using the API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Set OpenAI model and parameters
model_engine = "text-davinci-002"
max_tokens = 256

# Connect to or create the ontology database
ontology_storage = OntologyStorage()

def chat_with_anubis(input_text):
    # Get the persona for Anubis
    anubis_persona = get_persona("Anubis")

    # Set the prompt to include Anubis's persona and the user's input
    prompt = f"{anubis_persona}\nMorgan: {input_text}\nAnubis: "

    # Use OpenAI to generate a response to the prompt
    response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=max_tokens, temperature=0.5)

    # Extract the response text from the OpenAI response
    response_text = response.choices[0].text.strip()

    # Store the input and response in the ontology database
    ontology_storage.add_ontology(input_text, response_text)

    # Return the response text
    return response_text
