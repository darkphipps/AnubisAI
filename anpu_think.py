import re
import sqlite3

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

def extract_keywords(text):
    # Replace non-alphanumeric characters with spaces
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text)
    # Convert to lowercase
    text = text.lower()
    # Split into words
    words = text.split()
    # Remove stop words
    stop_words = ["the", "a", "an", "is", "of", "for", "and", "or", "in", "to"]
    words = [word for word in words if word not in stop_words]
    # Return unique keywords
    return set(words)

def anpu_think():
    # Connect to conversation database and retrieve the last input
    brain_conn = sqlite3.connect("anpu_brain.db")
    brain_cursor = brain_conn.cursor()
    brain_cursor.execute("SELECT input FROM conversation ORDER BY id DESC LIMIT 1")
    rows = brain_cursor.fetchall()
    if len(rows) > 0:
        last_input = rows[0][0]
    else:
        last_input = ""

    # Extract keywords from last input and add them to the mind database
    mind_storage = MindStorage()
    keywords = extract_keywords(last_input)
    mind_storage.add_keywords(keywords)

    # Use the mind database to organize the ontology
    ontology_storage = OntologyStorage()
    ontology_storage.organize_ontology(mind_storage.get_keywords())

if __name__ == "__main__":
    anpu_think()
