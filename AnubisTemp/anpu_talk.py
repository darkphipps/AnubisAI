import openai
import os
import textwrap
import sqlite3
from dotenv import load_dotenv

def anpu_talk(user_input, return_output=False):
    # Load environment variables from a .env file
    load_dotenv()

    # Authenticate with OpenAI using the API key
    openai.api_key = os.environ.get('OPENAI_API_KEY')

    # Set OpenAI model and parameters
    model_engine = "text-davinci-002"
    max_tokens = 64

    # Connect to or create the anpu_brain.db database
    brain_conn = sqlite3.connect("anpu_brain.db")
    brain_cursor = brain_conn.cursor()
    brain_cursor.execute('''CREATE TABLE IF NOT EXISTS conversation (id INTEGER PRIMARY KEY AUTOINCREMENT, input TEXT, output TEXT)''')

    # Connect to or create the anpu_mind.db database
    mind_conn = sqlite3.connect("anpu_mind.db")
    mind_cursor = mind_conn.cursor()
    mind_cursor.execute('''CREATE TABLE IF NOT EXISTS ontology (id INTEGER PRIMARY KEY AUTOINCREMENT, statement TEXT, response TEXT)''')

    # Define Anubis persona
    anubis_persona = "As the ancient Egyptian god of the dead, I am both mysterious and wise. Ask me anything and I will reveal the secrets of the afterlife."

    # Store input in the conversation database
    brain_cursor.execute("INSERT INTO conversation (input) VALUES (?)", (user_input,))
    brain_conn.commit()

    # Use Anubis persona to roleplay the response
    prompt = f"Anubis: {anubis_persona}\nMorgan: {user_input}\nAnubis: "

    # Use the prompt to generate a response using OpenAI
    response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=max_tokens)

    # Store the response in the conversation database
    brain_cursor.execute("UPDATE conversation SET output = ? WHERE id = ?", (response.choices[0].text, brain_cursor.lastrowid))
    brain_conn.commit()

    # Store the input and output in the ontology database
    mind_cursor.execute("INSERT INTO ontology (statement, response) VALUES (?, ?)", (user_input, response.choices[0].text))
    mind_conn.commit()

    # Return the output if requested
    if return_output:
        return response.choices[0].text
    else:
        # Print the response, wrapped at 100 characters
        print("Anubis: " + textwrap.fill(response.choices[0].text, width=100))

if __name__ == "__main__":
    user_input = input("Enter your message: ")
    output = anpu_talk(user_input, return_output=True)
    print("Anubis: " + textwrap.fill(output, width=100))
