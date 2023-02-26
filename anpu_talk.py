import openai
import os
import textwrap
from anpu_storage import ConversationStorage, OntologyStorage, MindStorage
from dotenv import load_dotenv
from anpu_persona import get_anubis_persona

def anpu_talk(user_input, return_output=False):
    # Load environment variables from a .env file
    load_dotenv()

    # Authenticate with OpenAI using the API key
    openai.api_key = os.environ.get('OPENAI_API_KEY')

    # Set OpenAI model and parameters
    model_engine = "text-davinci-002"
    max_tokens = 256

    # Connect to or create the conversation and ontology databases
    conversation_storage = ConversationStorage()
    ontology_storage = OntologyStorage()
    mind_storage = MindStorage()

    if not user_input:
        # If user_input is empty, return a default response
        default_response = "Please enter a message for me to respond to."
        if return_output:
            return default_response
        else:
            print("Anubis: " + textwrap.fill(default_response, width=100))
            return

    # Store input in the conversation database
    conversation_storage.add_conversation(user_input, "")

    # Use Anubis persona to roleplay the response
    prompt = f"Anubis: {get_anubis_persona()}\nMorgan: {user_input}\nAnubis: "

    # Use the prompt to generate a response using OpenAI
    response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=max_tokens)

    # Store the response in the conversation database
    conversation_storage.add_conversation("", response.choices[0].text)

    # Store the input and output in the ontology database
    ontology_storage.add_ontology(user_input, response.choices[0].text)

    # Use the ontology database to improve the response
    similar_response = ontology_storage.get_similar_responses(user_input)
    if similar_response is not None:
        response_text = similar_response
    else:
        response_text = response.choices[0].text

    # Use the mind database to improve the response further
    keywords = mind_storage.get_keywords()
    for keyword in keywords:
        if keyword in response_text:
            response_text = response_text.replace(keyword, f"[{keyword}]")

    # Store the improved response in the conversation database
    conversation_storage.add_conversation("", response_text)

    # Return the output if requested
    if return_output:
        return response_text
    else:
        # Print the response, wrapped at 100 characters
        print("Anubis: " + textwrap.fill(response_text, width=100))

if __name__ == "__main__":
    user_input = input("Enter your message: ")
    output = anpu_talk(user_input, return_output=True)
    print("Anubis: " + textwrap.fill(output, width=100))
