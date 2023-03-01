import re
import sqlite3
from anpu_similarity import calculate_similarity
import os


def create_or_reuse_database():
    """
    Creates or reuses the anpu_conversations.db database.
    """
    db_path = os.path.join(os.path.dirname(__file__), "anpu_conversations.db")
    conn = sqlite3.connect(db_path)

    # Check if the ontology_topics table exists
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ontology_topics';")
    table_exists = c.fetchone()

    if not table_exists:
        # Create the ontology_topics table if it doesn't exist
        c.execute('''
                  CREATE TABLE ontology_topics 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  topic TEXT UNIQUE);
                  ''')

    # Check if the ontology table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ontology';")
    table_exists = c.fetchone()

    if not table_exists:
        # Create the ontology table if it doesn't exist
        c.execute('''
                  CREATE TABLE ontology 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  topic_id INTEGER, 
                  response TEXT,
                  FOREIGN KEY (topic_id) REFERENCES ontology_topics(id));
                  ''')

    # Check if the mind table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mind';")
    table_exists = c.fetchone()

    if not table_exists:
        # Create the mind table if it doesn't exist
        c.execute('''
                  CREATE TABLE mind 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  persona TEXT,
                  keywords TEXT,
                  user_input TEXT, 
                  response TEXT);
                  ''')

    # Check if the conversations table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations';")
    table_exists = c.fetchone()

    if not table_exists:
        # Create the conversations table if it doesn't exist
        c.execute('''
                  CREATE TABLE conversations 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_input TEXT,
                  response_text TEXT);
                  ''')

    # Check if the chat_logs table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_logs';")
    table_exists = c.fetchone()

    if not table_exists:
        # Create the chat_logs table if it doesn't exist
        c.execute('''
                  CREATE TABLE chat_logs 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_input TEXT, 
                  response_text TEXT);
                  ''')

    # Commit the transaction
    conn.commit()

    return conn

class ConversationStorage:
    """
    Stores and retrieves conversations in a SQLite database.
    """
    def __init__(self, database="anpu_conversations.db"):
        self.conn = sqlite3.connect(database)
        self.create_table()

    def create_table(self):
        """
        Creates a 'conversations' table if it doesn't exist.
        """
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_input TEXT,
                     response_text TEXT)''')
        self.conn.commit()

    def add_conversation(self, user_input, response_text):
        """
        Adds a conversation to the database.
        """
        c = self.conn.cursor()
        c.execute("INSERT INTO conversations (user_input, response_text) VALUES (?, ?)", (user_input, response_text))
        self.conn.commit()

    def get_conversations(self):
        """
        Returns a list of all conversations in the database.
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM conversations")
        return c.fetchall()

class AnpuStorage:
    def __init__(self):
        self.conn = sqlite3.connect('anpu_conversations.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                response_text TEXT
            );
        ''')
        self.conn.commit()

    def store_conversation(self, user_input, response_text):
        self.cursor.execute('''
            INSERT INTO conversations (user_input, response_text) VALUES (?, ?);
        ''', (user_input, response_text))
        self.conn.commit()

    def get_conversations(self):
        self.cursor.execute('SELECT * FROM conversations;')
        rows = self.cursor.fetchall()
        return rows


class MindStorage:
    def __init__(self):
        self.conn = sqlite3.connect("anpu_mind.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS responses (id INTEGER PRIMARY KEY AUTOINCREMENT, response TEXT, persona TEXT)'''
        )
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS keywords (id INTEGER PRIMARY KEY AUTOINCREMENT, keyword TEXT, persona TEXT)'''
        )

    # ...

    def add_response(self, response, persona=None):
        self.cursor.execute("INSERT INTO responses (response, persona) VALUES (?, ?)", (response, persona))
        self.conn.commit()

    def get_similar_response(self, response_text, persona_name=None):
        self.cursor.execute("SELECT response FROM responses WHERE persona=?", (persona_name,))
        rows = self.cursor.fetchall()
        if rows:
            stored_responses = [row[0] for row in rows]
            similarity_scores = []
            for stored_response in stored_responses:
                similarity_score = calculate_similarity(response_text, stored_response)
                similarity_scores.append((similarity_score, stored_response))

            # Sort by similarity score (higher score first)
            similarity_scores.sort(reverse=True)

            # Return the response with the highest similarity score
            if similarity_scores:
                return similarity_scores[0][1]
        return None

    def add_keywords(self, keywords, persona=None):
        for keyword in keywords:
            self.cursor.execute("INSERT INTO keywords (keyword, persona) VALUES (?, ?)", (keyword, persona))
        self.conn.commit()

    def get_keywords(self, persona=None):
        if persona is None:
            self.cursor.execute("SELECT keyword FROM keywords")
        else:
            self.cursor.execute("SELECT keyword FROM keywords WHERE persona=?", (persona,))
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def get_keywords_by_persona(self, persona):
        self.cursor.execute("SELECT keyword FROM keywords WHERE persona=?", (persona,))
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]
class OntologyStorage:
    def __init__(self):
        self.conn = sqlite3.connect("anpu_ontology.db")
        self.conn.execute('PRAGMA journal_mode = OFF;')  # Disable journaling
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS ontology (id INTEGER PRIMARY KEY AUTOINCREMENT, input TEXT, output TEXT)''')

    def add_ontology(self, input_text, output_text):
        # Store the input and output texts in the ontology database
        self.cursor.execute("INSERT INTO ontology (input, output) VALUES (?, ?)", (input_text, output_text))
        self.conn.commit()

        # Print a message to indicate that the input and output texts were stored
        print(f"Stored '{input_text}' and '{output_text}' in the ontology database.")

    def get_similar_responses(self, input_text):
        self.cursor.execute("SELECT output FROM ontology")
        rows = self.cursor.fetchall()
        similarity_scores = []
        for row in rows:
            similarity_score = calculate_similarity(input_text, row[0])
            similarity_scores.append((similarity_score, row[0]))

        # Sort by similarity score (higher score first)
        similarity_scores.sort(reverse=True)

        # Return the response with the highest similarity score
        if similarity_scores:
            return similarity_scores[0][1]
        return None

    def organize_ontology(self, keywords, threshold=2):
        input_patterns = []
        for keyword in keywords:
            input_patterns.append('%' + keyword + '%')
        input_patterns = list(set(input_patterns))

        for pattern in input_patterns:
            self.cursor.execute("SELECT output FROM ontology WHERE input LIKE ?", (pattern,))
            rows = self.cursor.fetchall()
            if len(rows) < 2:
                continue
            for i in range(len(rows)):
                for j in range(i + 1, len(rows)):
                    row1 = rows[i]
                    row2 = rows[j]
                    if row1[0] == row2[0]:
                        continue
                    self.cursor.execute("SELECT COUNT(*) FROM ontology WHERE input=? AND output=?", (row1[0], row2[0]))
                    count = self.cursor.fetchone()[0]
                    if count >= threshold:
                        continue
                    self.cursor.execute("INSERT INTO ontology (input, output) VALUES (?, ?)", (row1[0], row2[0]))
                    self.conn.commit()

    def has_ontology_topic(self, topic):
        self.cursor.execute("SELECT COUNT(*) FROM ontology WHERE input LIKE ?", ('%' + topic + '%',))
        count = self.cursor.fetchone()[0]
        return count > 0



class StopWords:
    def __init__(self, filename):
        with open(filename, 'r') as file:
            self.words = [word.strip() for word in file]

    def is_stop_word(self, word):
        return word in self.words


def extract_keywords(text, stop_words):
    # Replace non-alphanumeric characters with spaces
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text)
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
