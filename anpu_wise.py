import sqlite3
from datetime import datetime
from anpu_extract import extract_keywords, extract_ontology_topics, StopWords
from anpu_similarity import calculate_similarity  # added import


class AnpuStorage:
    def __init__(self):
        self.mind_storage = MindStorage()
        self.ontology_storage = OntologyStorage()
        self.brain_storage = BrainStorage()

    def store_conversation(self, user_input, response_text):
        self.brain_storage.add_conversation(datetime.now(), None)
        self.brain_storage.add_message(self.brain_storage.get_last_conversation()["id"], "user", user_input)
        self.brain_storage.add_message(self.brain_storage.get_last_conversation()["id"], "Anubis", response_text)

        self.mind_storage.add_keywords(extract_keywords(user_input, stop_words))
        self.mind_storage.add_response(response_text)

        ontology_topics = extract_ontology_topics(user_input)
        for topic in ontology_topics:
            self.ontology_storage.add_ontology(topic, response_text)

        similar_response = self.mind_storage.get_similar_response(response_text)
        if similar_response is not None:
            return similar_response

        similar_response = self.ontology_storage.get_similar_responses(user_input)
        if similar_response is not None:
            return similar_response

        return response_text


class MindStorage:
    def __init__(self):
        self.conn = sqlite3.connect("anpu_mind.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS responses (id INTEGER PRIMARY KEY AUTOINCREMENT, response TEXT)'''
        )
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS keywords (id INTEGER PRIMARY KEY AUTOINCREMENT, keyword TEXT)'''
        )

    def add_response(self, response):
        self.cursor.execute("INSERT INTO responses (response) VALUES (?)", (response,))
        self.conn.commit()

    def get_similar_response(self, response_text):
        self.cursor.execute("SELECT response FROM responses")
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
            for i in range(len(rows)):
                for j in range(i + 1, len(rows)):
                    row1 = rows[i]
                    row2 = rows[j]
                    if row1[0] == row2[0]:
                        continue
                    self.cursor.execute("SELECT COUNT(*) FROM ontology WHERE input=? AND output=?", (row1[0], row2[0]))
                    count = self.cursor.fetchone()[0]
                    if count >= 2:
                        continue
                    self.cursor.execute("INSERT INTO ontology (input, output) VALUES (?, ?)", (row1[0], row2[0]))
                    self.conn.commit()
