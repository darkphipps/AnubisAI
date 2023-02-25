import sqlite3


class ConversationStorage:
    def __init__(self):
        self.conn = sqlite3.connect("anpu_brain.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS conversation (id INTEGER PRIMARY KEY AUTOINCREMENT, input TEXT, output TEXT)''')

    def add_conversation(self, input_text, output_text):
        self.cursor.execute("INSERT INTO conversation (input, output) VALUES (?, ?)", (input_text, output_text))
        self.conn.commit()


class OntologyStorage:
    def __init__(self):
        self.conn = sqlite3.connect("anpu_mind.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS ontology (id INTEGER PRIMARY KEY AUTOINCREMENT, statement TEXT, response TEXT)''')

    def add_ontology(self, statement_text, response_text):
        self.cursor.execute("INSERT INTO ontology (statement, response) VALUES (?, ?)", (statement_text, response_text))
        self.conn.commit()

    def update_ontology(self, statement_text, response_text):
        self.cursor.execute("UPDATE ontology SET response = ? WHERE statement = ?", (response_text, statement_text))
        self.conn.commit()

    def get_similar_responses(self, statement_text):
        self.cursor.execute("SELECT response FROM ontology WHERE statement LIKE ?", ('%' + statement_text + '%',))
        rows = self.cursor.fetchall()
        if len(rows) > 0:
            return rows[0][0]
        else:
            return None
