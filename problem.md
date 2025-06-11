# Problem 
Got an email saying to solve the below problem:

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
 
The script is really simple so there is quite a lot of approaches I can take. The first my mind has gone to is can I create a Olamma docker image to write the sparql query for me? The easier method is to prewrite the queries and then just use old or population to split the category of questions. 

Plan:
 - Read about wikidata
 - Read how querying works for wikidata
 - Look into wikidata sparql queries. 
 - Research if any smart people have made a premade NLP tool. 


# Solution help

- I found a website wikidata query service which allows me to test out queries quickly and get live feedback on what they are retrieving. 
    - Tom Cruise seems to lack date of birth from inital looking. 
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

    - This raises two issues I need to categorise the question. I can do this by rule based approach or I could use a tinyLLM? I have a script already made. I'm really tempted to just check if I could get tinyLLMs to do this. 