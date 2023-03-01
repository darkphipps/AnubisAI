import openai
import os
import sqlite3
import textwrap
from dotenv import load_dotenv
from anpu_extract import extract_keywords
from anpu_persona import get_persona
from anpu_storage import OntologyStorage, MindStorage, ConversationStorage

# Load environment variables from a .env file
load_dotenv()

# Authenticate with OpenAI using the API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Set OpenAI model and parameters
model_engine = "text-davinci-002"
max_tokens = 64

# Connect to or create the ontology and mind databases
ontology_storage = OntologyStorage()
mind_storage = MindStorage()
conversation_storage = ConversationStorage()

# Load stop words from a file
stop_words_file = os.path.join(os.path.dirname(__file__), "anpu_stopwords.txt")
with open(stop_words_file, "r") as f:
    stop_words = set(f.read().splitlines())


def generate_openai_prompt(user_input, persona_name, stop_words=None):
    """
    Generates an OpenAI prompt based on the user input and persona name.
    """
    persona = get_persona(persona_name)
    prompt_prefix = f"{persona}\n{user_input}\n"

    # Generate prompt suffix
    if ontology_storage.has_ontology_topic("Egyptian mythology"):
        prompt_suffix = "In Egyptian mythology, "
    else:
        prompt_suffix = ""

    # Combine the prompt prefix and suffix
    prompt = f"{prompt_prefix}{prompt_suffix}"

    return prompt


def generate_response(user_input, persona_name="Anubis", max_tokens=50, stop_words=None, keywords=None):
    if stop_words is None:
        stop_words = set()
    if keywords is None:
        keywords = []

    # rest of the function code here...
    prompt = generate_openai_prompt(user_input, persona_name, stop_words)

    # Generate response using OpenAI API
    response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=max_tokens, n=3)

    # Extract the response text from the API response
    response_text = response.choices[0].text.strip()

    # Store the conversation in the ontology database
    conversation_storage.add_conversation(user_input, response_text)

    # Return the response text
    return response_text


def improve_response_with_ontology(user_input, response_text):
    """
    Uses the ontology database to improve the response.
    """
    similar_responses = ontology_storage.get_similar_responses(user_input)
    if similar_responses is not None:
        similar_responses = set(similar_responses.split("\n"))
        if response_text.strip() in similar_responses:
            similar_responses.remove(response_text.strip())
        if len(similar_responses) > 0:
            response_text = similar_responses.pop()
    return response_text


def improve_response_with_mind(response_text, persona_name="Anubis"):
    """
    Uses the mind database to improve the response.
    """
    improved_response = mind_storage.get_similar_response(response_text, persona_name=persona_name)
    if improved_response is not None:
        response_text = improved_response
    return response_text
def store_in_ontology(user_input, response_text, ontology_storage_conn):
    # Check if the chat_logs table exists in the ontology storage connection
    c = ontology_storage_conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_logs';")
    table_exists = c.fetchone()

    if table_exists:
        # Insert the user input and response into the chat_logs table
        c.execute("INSERT INTO chat_logs (user_input, response_text) VALUES (?, ?)", (user_input, response_text))
    else:
        # Create the chat_logs table if it doesn't exist
        c.execute('''
                  CREATE TABLE IF NOT EXISTS chat_logs 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_input TEXT, 
                  response_text TEXT);
                  ''')
        c.execute("INSERT INTO chat_logs (user_input, response_text) VALUES (?, ?)", (user_input, response_text))

    # Commit the transaction
    ontology_storage_conn.commit()

def anpu_talk(user_input, persona=None, default_persona_name="Anubis"):
    if persona is None:
        persona_name = default_persona_name
    else:
        persona_name = persona

    # Get keywords for the persona
    mind_storage = MindStorage()
    keywords_str = mind_storage.get_keywords_by_persona(persona_name)
    keywords = keywords_str.split(",") if keywords_str else []

    # Add user input to conversation log
    conversation_storage.add_conversation(user_input, "")

    # Check if user input matches any stored responses
    improved_response = mind_storage.get_similar_response(user_input, persona_name=persona_name)

    if improved_response:
        conversation_storage.add_conversation(user_input, improved_response)
        return improved_response

    # Otherwise, generate a new response using the persona ontology
    response_text = generate_response(user_input, persona_name, max_tokens, stop_words, keywords)

    # Improve response with ontology
    response_text = improve_response_with_ontology(user_input, response_text)

    # Improve response with mind
    response_text = improve_response_with_mind(response_text, persona_name)

    # Add response to conversation log
    conversation_storage.add_conversation(user_input, response_text)

    return response_text
