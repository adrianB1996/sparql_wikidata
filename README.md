# SPARQL Wikidata Query Tool

A simple Python tool for querying Wikidata using SPARQL.

## Table of Contents
- [SPARQL Wikidata Query Tool](#sparql-wikidata-query-tool)
- [Prerequisites](#prerequisites)
  - [For Docker Usage](#for-docker-usage)
  - [For LLM Model Usage](#for-llm-model-usage)
- [Installation](#installation)
- [Running the Script](#running-the-script)
- [Running with Docker](#running-with-docker)
- [Viewing the Frontend](#viewing-the-frontend)
- [SPARQL Wikidata Query Tool: What It Supports](#sparql-wikidata-query-tool-what-it-supports)
  - [What Works Reliably](#what-works-reliably)
    - [Supported Examples](#supported-examples)
      - [1. Person’s Date of Birth](#1-persons-date-of-birth)
      - [2. City Population](#2-city-population)
      - [3. Country’s Head of State](#3-countrys-head-of-state)
  - [Usage Notes & Limitations](#usage-notes--limitations)
- [Summary](#summary)

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### For Docker Usage

- [Docker](https://www.docker.com/get-started) (version 19.03.0 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 1.25.0 or higher)
- At least 2GB of RAM available for Docker
- Internet connection (for downloading Docker images and querying Wikidata)

### For LLM Model Usage

- Sufficient disk space and RAM for model weights (varies by model, typically 4GB+ RAM and 4GB+ disk)
- If using GPU acceleration: CUDA-compatible GPU and drivers installed
- Downloaded LLM model files (see project documentation or model provider for details)
- Set environment variables or configuration files to point to the model location if required

## Installation

1. Clone or download this repository:
   ```bash
   git clone https://github.com/adrianB1996/sparql_wikidata.git
   cd sparql_wikidata
   ```
2. Move into the solution folder in your local solution (if not already there):
   ```bash
   cd solution
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Script

To run the Wikidata query tool:

```bash
python query_wikidata.py
```
## Running with Docker

1. Ensure Docker and Docker Compose are installed and running.
2. Build and start the service:
   ```bash
   docker compose build --no-cache
   ```
3. To run just the main script in a container for the interview question (You may need to run it twice if the container is warming up :):
   ```bash
   docker compose run --rm dash-app python query_wikidata.py
   ```

4. To run the frontend and backend. This will take awhile as the models and manifests will need to be pulled through:
   ```bash
   docker compose up
   ```

5. To stop the service:
   ```bash
   docker compose down
   ```

## Viewing the Frontend

- Open your browser and go to: [http://localhost:8050](http://localhost:8050)
- If you changed the port in your Docker or application configuration, use that port instead.
- You can try out the preselected options or you can try the SPARQL query generator. It can answer about other people or places. (It's very rough)
- Write in a simple question
- click generate sparQL --> This will generate a query and check it's formatted correctly. 
- get results and interpret. 
- I just wanted to see what I could do with a tiny model. 
- It can take a little while to interpret the result and respond. 


# SPARQL Wikidata Query Tool: What It Supports

This tool uses a small language model to help you generate SPARQL queries for Wikidata using natural language.
**It is designed only for specific simple query types shown in its model file.** See details below.

## What Works Reliably

This tool can reliably answer **only the exact question patterns included in its model file**.
Anything beyond these—such as combining filters, asking for data not shown in the examples, or using different phrasing—is **not supported**.

**You can ask about different people, cities, or countries—just make sure your question follows the same structure as the examples below.**
For instance, you can substitute Tom Cruise with another actor (e.g., "How old is Brad Pitt?"), London with another city, or France with another country.
As long as you stick to the exact pattern, you can use any specific name or place.

### Supported Examples

#### 1. Person’s Date of Birth

How old is Tom Cruise? *(works for any actor, musician, etc. if you use this format)*

```sparql
SELECT ?date_of_birth WHERE {
  ?person rdfs:label "Tom Cruise"@en ;
          wdt:P569 ?date_of_birth .
}
LIMIT 1
```


#### 2. City Population

What is the population of London? *(works for any city if you use this format)*

```sparql
SELECT ?population WHERE {
  ?location rdfs:label "London"@en ;
            wdt:P1082 ?population .
}
ORDER BY DESC(?population)
LIMIT 1
```


#### 3. Country’s Head of State

Who is the president of France? *(works for any country if you use this format)*

```sparql
SELECT ?president ?presidentLabel WHERE {
  ?country rdfs:label "France"@en ;
           wdt:P35 ?president .
  ?president rdfs:label ?presidentLabel .
  FILTER(LANG(?presidentLabel) = "en")
}
LIMIT 1
```


## Usage Notes \& Limitations

- **Only the above formats (or very close variants) will reliably work.**
- You can swap in different names, cities, or countries—just keep the question’s structure identical to the examples.
- For any other question type—even if only a little more complex or phrased differently—this tool is **not likely** to produce a working SPARQL query.
- If your straightforward query doesn’t work the first time, try rerunning it. Sometimes a second run resolves initial mistakes.
- Complex or multi-step queries (for example, filtering by date, combining several properties, or using information about more than one entity) are not supported—even if similar queries are included as examples in the prompt.

| What Works Best | Examples |
| :-- | :-- |
| Single property for an entity | Tom Cruise’s birth date, Brad Pitt’s birth date, Beyoncé’s birth date |
| Simple statistic for a place | London’s population, Tokyo’s population |
| Relationship for one country | President of France, Head of State of Germany |

## Summary

**This tool is for simple, specific fact lookups only, using question types already found in its examples above.**
For anything else, SPARQL query results will be unpredictable or simply not returned.

If in doubt, copy your question to match the style of the working examples above, but feel free to use any other person, city, or country name.

*Questions, feedback, or issues? Please open an issue or pull request!*




![alt text](image.png)
