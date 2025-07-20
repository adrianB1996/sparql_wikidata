# Problem to solve
```
def ask(question: str, endpoint: str = 'https://query.wikidata.org/sparql'):
     # please complete this method however you wish
     pass

if _name_ == '_main_':
    assert '62' == ask('how old is Tom Cruise')
    assert '35' == ask('how old is Taylor Swift')
    assert '8799728' == ask('what is the population of London')
    assert '8804190' == ask('what is the population of New York?')
```

# Questions

- What is wikidata?
- What structure is the wikidata KG? 
- Solutions?

# Ideation 
 
The script is really simple so there is quite a lot of approaches I can take. The first my mind has gone to is can I create a Olamma docker image to write the sparql query for me? The easier method is to prewrite the queries and then just use age/old or population to split the category of questions. 

Plan:
 - Read about wikidata
 - Read how querying works for wikidata
 - Look into wikidata sparql queries. 
 - Research if any smart people have made a premade NLP tool. 


# Solution help

- I found a website wikidata query service which allows me to test out queries quickly and get live feedback on what they are retrieving. 
    - Found it using 
    ```
    SELECT ?date_of_birth WHERE {
  ?person rdfs:label "Tom Cruise"@en ;
          wdt:P569 ?date_of_birth .
        }
        LIMIT 1
    ```
    - This gives:
    ```
        3 July 1962
    ```

    - This raises two issues:
    
    - I need to calculate birth date from dd/month/year
    - I need to categorise the question. I can do this by rule based approach.
    - This should also work for Taylor Swift

- Population and location query I have found to work for New York using where location name is New York City to match the number required:
    ```
    SELECT ?population WHERE {{
        ?location rdfs:label "{location_name}"@en ;
                    wdt:P1082 ?population .
        }}
        ORDER BY DESC(?population)
        LIMIT 1
    ```

    - How I found this out by was googling wiki data new york with the number. 
    - London recieves multiple results but the result that the interview question in looking for is associated with wd:Q84.

# Explaining the project

- I wanted to see if I could create a automatic sparlql query generator that would work on most peoples pc's locally.
