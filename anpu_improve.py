from anpu_storage import OntologyStorage, MindStorage

# Connect to the ontology and mind databases
ontology_storage = OntologyStorage()
mind_storage = MindStorage()

def improve_response_with_ontology(user_input, response_text):
    """
    Uses the ontology database to improve the response.
    """
    similar_response = ontology_storage.get_similar_responses(user_input)
    if similar_response is not None and similar_response != response_text.strip():
        response_text = similar_response
    return response_text

def improve_response_with_mind(response_text, persona_name):
    # Use the current persona to retrieve keywords associated with that persona from the mind database
    persona_keywords = mind_storage.get_keywords_by_persona(persona_name)

    # Replace keywords in the response with the same keywords surrounded by brackets
    for keyword in persona_keywords:
        if keyword in response_text:
            response_text = response_text.replace(keyword, f"[{keyword}]")

    return response_text
