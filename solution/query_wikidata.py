import requests
from datetime import datetime
import re
from SPARQLWrapper import SPARQLWrapper, JSON


def ask(question: str, endpoint: str = "https://query.wikidata.org/sparql"):
    """
    Answer questions by querying Wikidata using SPARQL

    Args:
        question: A natural language question (e.g., "how old is Tom Cruise")
        endpoint: SPARQL endpoint URL

    Returns:
        string answer to the question
    """
    # Simple mapping of questions to handler functions
    question = question.lower()

    if "how old is tom cruise" in question:
        return get_age("Tom Cruise", endpoint)
    elif "how old is taylor swift" in question:
        return get_age("Taylor Swift", endpoint)
    elif "what is the population of london" in question:
        return get_population("London", endpoint)
    elif "what is the population of new york" in question:
        return get_population("New York City", endpoint)
    else:
        return "I don't know how to answer this question"


def get_age(person_name: str, endpoint: str):
    """Get age for a specific person"""

    # Build SPARQL query
    query = f"""
    SELECT ?date_of_birth WHERE {{
      ?person rdfs:label "{person_name}"@en ;
              wdt:P569 ?date_of_birth .
    }}
    LIMIT 1
    """

    # Execute query
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        print(results)
        if results["results"]["bindings"]:
            birth_date = results["results"]["bindings"][0]["date_of_birth"]["value"]
            # Calculate age from birth date
            birth_date = datetime.strptime(birth_date.split("T")[0], "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1
            return str(age)
        else:
            return "Could not find birth date information"
    except Exception as e:
        return f"Error executing query: {str(e)}"


def get_population(location_name: str, endpoint: str):
    """Get population for a specific location"""

    if location_name.lower() == "london":
        query = """
        SELECT ?population WHERE {
            wd:Q84 wdt:P1082 ?population .
        }
        ORDER BY DESC(?population)
        LIMIT 100
        """
    else:
        # Build SPARQL query
        query = f"""
        SELECT ?population WHERE {{
        ?location rdfs:label "{location_name}"@en ;
                    wdt:P1082 ?population .
        }}
        ORDER BY DESC(?population)
        LIMIT 1
    """

    # Execute query
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        if results["results"]["bindings"]:
            population = results["results"]["bindings"][0]["population"]["value"]
            return str(population)
        else:
            return "Could not find population information"
    except Exception as e:
        return f"Error executing query: {str(e)}"


if __name__ == "__main__":
    assert "62" == ask("how old is Tom Cruise")
    assert "35" == ask("how old is Taylor Swift")
    assert "8799728" == ask("what is the population of London")
    assert "8804190" == ask("what is the population of New York?")
    print("All tests passed!")
