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


def anpu_think(response, user_input):
    # Extract keywords from user input and add them to the mind database
    mind_storage = MindStorage()
    keywords = extract_keywords(user_input, StopWords('stopwords.txt'))
    mind_storage.add_keywords(keywords)

    # Use the mind database to organize the ontology
    ontology_storage = OntologyStorage()
    ontology_storage.organize_ontology(mind_storage.get_keywords())

    # Use the ontology database to improve the response
    similar_response = ontology_storage.get_similar_responses

stop_words = StopWords('stopwords.txt')