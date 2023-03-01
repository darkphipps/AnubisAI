import re

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

stop_words = StopWords("anpu_stopwords.txt")
