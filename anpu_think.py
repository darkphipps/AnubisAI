import re
import sqlite3
import openai
from anpu_extract import extract_keywords
import anpu_storage

class MindStorage:
    def __init__(self):
        self.conn = sqlite3.connect("anpu_mind.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS keywords (id INTEGER PRIMARY KEY AUTOINCREMENT, keyword TEXT)''')

    def add_keywords(self, keywords):
        for keyword in keywords:
            self.cursor.execute("INSERT INTO keywords (keyword) VALUES (?)", (keyword,))
        self.conn.commit()

    def get_keywords(self):
        self.cursor.execute("SELECT keyword FROM keywords")
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def create_ontology_from_conversations(self):
        # Get all conversations from the brain database
        brain_storage = BrainStorage()
        conversations = brain_storage.get_all_conversations()

        # Extract unique keywords from all conversations
        all_keywords = set()
        for conversation in conversations:
            for message in conversation["messages"]:
                text = message["text"]
                stop_words = StopWords("anpu_stopwords.txt")
                keywords = extract_keywords(text, stop_words)
                all_keywords.update(keywords)

        # Create an ontology from the keywords
        ontology_storage = OntologyStorage()
        ontology_storage.organize_ontology(list(all_keywords))


class OntologyStorage:
    def __init__(self):
        self.conn = sqlite3.connect("anpu_ontology.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS ontology (id INTEGER PRIMARY KEY AUTOINCREMENT, input TEXT, output TEXT)''')

    def add_ontology(self, input_text, output_text):
        self.cursor.execute("INSERT INTO ontology (input, output) VALUES (?, ?)", (input_text, output_text))
        self.conn.commit()

    def get_similar_responses(self, input_text):
        self.cursor.execute("SELECT output FROM ontology WHERE input LIKE ?", ('%' + input_text + '%',))
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            return None
        else:
            return rows[0][0]

    def organize_ontology(self, keywords):
        input_patterns = []
        for keyword in keywords:
            input_patterns.append('%' + keyword + '%')
        input_patterns = list(set(input_patterns))

        for pattern in input_patterns:
            self.cursor.execute("SELECT output FROM ontology WHERE input LIKE ?", (pattern,))
            rows = self.cursor.fetchall()
            if len(rows) < 2:
                continue
            for row1 in rows:
                for row2 in rows:
                    if row1[0] == row2[0]:
                        continue
                    self.cursor.execute("SELECT * FROM ontology WHERE input=? AND output=?", (row2[0], row1[0]))
                    if not self.cursor.fetchone():
                        self.cursor.execute("INSERT INTO ontology (input, output) VALUES (?, ?)", (row1[0], row2[0]))
                        self.conn.commit()


class BrainStorage:
    def __init__(self):
        self.conn = sqlite3.connect("anpu_brain.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, start_time TEXT, end_time TEXT)''')
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id INTEGER, speaker TEXT, text TEXT)''')

    def add_conversation(self, start_time, end_time):
        self.cursor.execute("INSERT INTO conversations (start_time, end_time) VALUES (?, ?)", (start_time, end_time))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_message(self, conversation_id, speaker, text):
        self.cursor.execute("INSERT INTO messages (conversation_id, speaker, text) VALUES (?, ?, ?)", (conversation_id, speaker, text))
        self.conn.commit()

    def get_conversation(self, conversation_id):
        self.cursor.execute("SELECT * FROM conversations WHERE id=?", (conversation_id,))
        conversation_row = self.cursor.fetchone()
        if conversation_row is None:
            return None
        conversation = {"id": conversation_row[0], "start_time": conversation_row[1], "end_time": conversation_row[2], "messages": []}
        self.cursor.execute("SELECT * FROM messages WHERE conversation_id=?", (conversation_id,))
        message_rows = self.cursor.fetchall()
        for message_row in message_rows:
            message = {"id": message_row[0], "speaker": message_row[2], "text": message_row[3]}
            conversation["messages"].append(message)
        return conversation

    def get_all_conversations(self):
        self.cursor.execute("SELECT id FROM conversations")
        conversation_ids = self.cursor.fetchall()
        conversations = []
        for conversation_id in conversation_ids:
            conversation = self.get_conversation(conversation_id[0])
            if conversation is not None:
                conversations.append(conversation)
        return conversations

    def get_last_conversation(self):
        self.cursor.execute("SELECT id FROM conversations ORDER BY id DESC LIMIT 1")
        conversation_id = self.cursor.fetchone()
        if conversation_id is not None:
            return self.get_conversation(conversation_id[0])
        else:
            return None

class StopWords:
    def __init__(self, filename):
        with open(filename, 'r') as file:
            self.words = [word.strip() for word in file]

    def is_stop_word(self, word):
        return word in self.words


def extract_keywords(text, stop_words):
    # Replace non-alphanumeric characters with spaces
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text)
    #

    # Convert to lowercase
    text = text.lower()
    # Split into words
    words = text.split()
    # Remove stop words
    words = [word for word in words if not stop_words.is_stop_word(word)]
    # Return unique keywords
    return set(words)


def extract_ontology_topics(text):
    # Extract topics surrounded by brackets
    pattern = r"\[([^\]]+)\]"
    matches = re.findall(pattern, text)
    return matches


def anpu_think(user_input):
    import os

    # Authenticate with OpenAI using the API key
    openai.api_key = os.environ.get('OPENAI_API_KEY')

    # Set OpenAI model and parameters
    model_engine = "text-davinci-002"
    max_tokens = 256

    # Create an instance of MindStorage
    mind_storage = MindStorage()

    # Extract keywords from the user input
    stop_words = StopWords("anpu_stopwords.txt")
    keywords = extract_keywords(user_input, stop_words)

    # Add keywords to the mind database
    mind_storage.add_keywords(keywords)

    # Use the ontology database to find a similar input and output
    similar_output = OntologyStorage().get_similar_responses(user_input)

    # Set up loop check
    conversation = BrainStorage().get_last_conversation()
    if conversation is not None:
        last_message = conversation["messages"][-1]["text"]
        if user_input == last_message and similar_output is not None:
            return similar_output

    # Use OpenAI to generate a response
    response = openai.Completion.create(engine=model_engine, prompt=user_input, max_tokens=max_tokens)

    # Use the response from OpenAI
    response_text = response.choices[0].text

    # Store the user input and response in the ontology database
    OntologyStorage().add_ontology(user_input, response_text)

    # Store the user input and response in the brain database
    conversation_id = BrainStorage().add_conversation(datetime.now(), None)
    BrainStorage().add_message(conversation_id, "user", user_input)
    BrainStorage().add_message(conversation_id, "Anubis", response_text)

    # Return the response
    return response_text




stop_words = StopWords('anpu_stopwords.txt')