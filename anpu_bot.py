import openai
import os
from dotenv import load_dotenv
from anpu_god_chat import chat_with_anubis
from anpu_mind_chat import chat_with_mind

# Load environment variables from a .env file
load_dotenv()

# Authenticate with OpenAI using the API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Set OpenAI model and parameters
model_engine = "text-davinci-002"
max_tokens = 64

# Define a function to handle user input and generate a response
def generate_response(user_input):
    # Check for keywords related to Anubis and chat with him
    if "Anubis" in user_input:
        response = chat_with_anubis(user_input)
    # Otherwise, chat with Anpu's mind
    else:
        response = chat_with_mind(user_input)

    return response

# Define a function to handle user input and print a response
def chat_with_bot():
    # Print welcome message
    print("Hello! I am Anpu, an AI designed to help you with your tasks.")

    # Start the chat loop
    while True:
        # Get user input
        user_input = input("You: ")

        # Generate a response
        response = generate_response(user_input)

        # Print the response
        print("Anpu:", response)

if __name__ == '__main__':
    # Start the chat with the bot
    chat_with_bot()
