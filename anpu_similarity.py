import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(response_text, stored_response):
    """
    Calculates the cosine similarity between two strings using the CountVectorizer and cosine_similarity functions
    from scikit-learn.
    """
    if not response_text or not stored_response:
        return 0

    # Create a CountVectorizer object to convert the text into a matrix of token counts
    vectorizer = CountVectorizer().fit_transform([response_text, stored_response])

    # Calculate the cosine similarity between the two vectors
    cosine_similarities = cosine_similarity(vectorizer[0], vectorizer[1])

    # Convert the cosine similarity score from a matrix to a scalar value
    similarity_score = np.round(cosine_similarities[0][0], 2)

    return similarity_score
