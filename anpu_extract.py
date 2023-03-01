import re
from anpu_stopwords import StopWords

def extract_keywords(text, stop_words):

    """
    Extracts keywords from a given text string.

    Args:
        text (str): The text to extract keywords from.

    Returns:
        A set of unique keywords extracted from the text.
    """
    # Create a StopWords instance to filter out stop words
    stop_words = StopWords("anpu_stopwords.txt")

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
