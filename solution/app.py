import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from query_wikidata import ask
import json

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Define predefined questions
questions = {
    "tom-cruise-age": "how old is Tom Cruise",
    "taylor-swift-age": "how old is Taylor Swift",
    "london-population": "what is the population of London",
    "new-york-population": "what is the population of New York"
}

# Define the app layout with both buttons and NL-to-SPARQL section
app.layout = dbc.Container([
    html.H1("Wikidata Question Answering", className="mt-4 mb-4 text-center"),
    
    # Predefined questions section
    dbc.Card([
        dbc.CardBody([
            html.H4("Predefined Questions:", className="mb-3"),
            
            html.Div([
                html.H5("Age Questions:", className="mt-3 mb-2"),
                dbc.ButtonGroup([
                    dbc.Button("How old is Tom Cruise?", id="tom-cruise-age", 
                               color="primary", className="me-2 mb-2"),
                    dbc.Button("How old is Taylor Swift?", id="taylor-swift-age", 
                               color="primary", className="me-2 mb-2"),
                ], className="mb-3"),
                
                html.H5("Population Questions:", className="mt-3 mb-2"),
                dbc.ButtonGroup([
                    dbc.Button("What is the population of London?", id="london-population", 
                               color="success", className="me-2 mb-2"),
                    dbc.Button("What is the population of New York?", id="new-york-population", 
                               color="success", className="me-2 mb-2"),
                ], className="mb-3"),
            ]),
            
            html.Div([
                html.H5("Selected Question:", className="mt-4"),
                html.Div(id="selected-question", className="p-2 border rounded mb-3 font-italic"),
                
                html.H5("Answer:",
                        style={"margin-top": "20px"}),
                html.Div(id="answer-output", className="p-3 border rounded")
            ])
        ])
    ], className="mt-3 mb-5"),
    
    # New Natural Language to SPARQL section
    dbc.Card([
        dbc.CardBody([
            html.H4("Natural Language to SPARQL Generator", className="mb-3"),
            html.P("Type any question and Qwen models will convert it to a SPARQL query for Wikidata:", className="text-muted"),
            
            dbc.Textarea(
                id="nl-input",
                placeholder="E.g., How Old is Tom Cruise?",
                className="mb-3",
                style={"height": "80px"}
            ),
            
            dbc.Button(
                "Generate SPARQL", 
                id="generate-sparql-btn", 
                color="info", 
                className="mb-4"
            ),
            
            html.Div([
                html.H5("Generated SPARQL Query:", className="mt-3"),
                dbc.Textarea(
                    id="sparql-query-output",
                    className="mb-3",
                    style={"height": "200px", "font-family": "monospace"},
                    readOnly=False  # Allow users to edit the query if needed
                ),
                
                dbc.Button([
                    "Execute Query ",
                    html.Span(id="query-validation-icon", className="ms-1")
                ], 
                    id="execute-sparql-btn", 
                    color="success", 
                    className="mb-4",
                    disabled=True  # Initially disabled until query is generated
                ),
                
                html.H5("Query Results:", className="mt-4"),
                html.Div(id="sparql-results-output", className="p-3 border rounded"),
                
                # Add interpretation section
                html.Div([
                    html.H5("Results Interpretation:", className="mt-4"),
                    dbc.Spinner(html.Div(id="results-interpretation", className="p-3 border rounded bg-light")),
                ], id="interpretation-section", style={"display": "none"}),
            ], id="query-section", style={"display": "none"})  # Initially hidden
        ])
    ], className="mt-3 mb-5"),
    
    html.Footer([
        html.Hr(),
        html.P("Wikidata SPARQL Query Service - Using SPARQLWrapper & Qwen", className="text-center text-muted")
    ])
], fluid=True, className="py-3")

# Updated callback to handle button clicks
@app.callback(
    [Output("selected-question", "children"),
     Output("answer-output", "children")],
    [Input(btn_id, "n_clicks") for btn_id in questions.keys()],
    prevent_initial_call=True
)
def update_output(*args):
    # Identify which button was clicked
    ctx = callback_context
    if not ctx.triggered:
        return "No question selected.", "Please select a question."
    
    # Get the ID of the clicked button
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Get the corresponding question
    if button_id in questions:
        question = questions[button_id]
        
        try:
            result = ask(question)
            return question, result
        except Exception as e:
            return question, f"Error: {str(e)}"
    
    return "Invalid question selected.", "Please select a valid question."

# Split the callback into two parts
# First callback: Generate SPARQL query from natural language
@app.callback(
    [Output("sparql-query-output", "value"),
     Output("query-section", "style"),
     Output("execute-sparql-btn", "disabled"),
     Output("sparql-results-output", "children")],  # Added this output to match return values
    Input("generate-sparql-btn", "n_clicks"),
    State("nl-input", "value"),
    prevent_initial_call=True
)
def generate_sparql(n_clicks, question):
    if not question:
        return "", {"display": "none"}, True, ""
    
    try:
        # Step 1: Generate the initial SPARQL query
        formatted_prompt = f"""Generate a SPARQL query for the following question do not include PREFIXes or explanations, just the query:
{question}"""
        
        response = requests.post(
            "http://ollama:11434/api/generate",
            json={
                "model": "sparql-helper",
                "prompt": formatted_prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return f"Error from LLM: {response.text}", {"display": "block"}, True, ""
        
        # Extract the SPARQL query from the response
        generated_query = response.json().get('response', '').strip()
        
        # Clean the response - extract just the SPARQL part if needed
        import re
        
        # Try to extract code blocks if present
        sparql_match = re.search(r'```(?:sparql)?(.*?)```', generated_query, re.DOTALL)
        if sparql_match:
            generated_query = sparql_match.group(1).strip()
        
        # Step 2: Test if the query works by executing it
        try:
            # Try to execute the query
            sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
            sparql.setQuery(generated_query)
            sparql.setReturnFormat(JSON)
            test_results = sparql.query().convert()
            
            # If we get here, the query works!
            query_works = True
            
        except Exception as test_error:
            # Query failed - capture the error
            query_works = False
            error_message = str(test_error)
            print(f"Query test failed: {error_message}")
            
            # Step 3: If query doesn't work, ask LLM to fix it
            fix_prompt = f"""
            The following SPARQL query is not working against Wikidata:
            ```
            {generated_query}
            ```
            
            Error message: {error_message}
            
            Please fix the query so it will work with Wikidata's SPARQL endpoint.
            Return ONLY the corrected query without any explanations.
            """
            
            fix_response = requests.post(
                "http://ollama:11434/api/generate",
                json={
                    "model": "sparql-helper",
                    "prompt": fix_prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if fix_response.status_code == 200:
                fixed_query = fix_response.json().get('response', '').strip()
                
                # Clean the fixed query
                sparql_match = re.search(r'```(?:sparql)?(.*?)```', fixed_query, re.DOTALL)
                if sparql_match:
                    fixed_query = sparql_match.group(1).strip()
                
                # Use the fixed query
                generated_query = fixed_query
                
                # Empty status - no message needed
                query_status = ""
            else:
                # If fixing failed, show no message
                query_status = ""
        else:
            # Query works fine - just set an empty string as we'll modify the button directly
            query_status = ""
        
        # Return value sets the execute button to enabled (False) and adds a checkmark if query works
        return generated_query, {"display": "block"}, False, query_status
        
    except Exception as e:
        return f"Error generating query: {str(e)}", {"display": "block"}, True, ""

# Second callback: Execute the SPARQL query
@app.callback(
    [Output("sparql-results-output", "children", allow_duplicate=True),  # Add allow_duplicate=True here
     Output("interpretation-section", "style"),
     Output("results-interpretation", "children")],
    Input("execute-sparql-btn", "n_clicks"),
    [State("sparql-query-output", "value"),
     State("nl-input", "value")],  # Also get the original question
    prevent_initial_call=True
)
def execute_sparql(n_clicks, query, original_question):
    if not query:
        return "No query to execute.", {"display": "none"}, ""
    
    try:
        # Execute the query against Wikidata
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        
        results = sparql.query().convert()
        
        # Format the results as a readable table
        if 'results' in results and 'bindings' in results['results']:
            bindings = results['results']['bindings']
            if not bindings:
                return "No results found.", {"display": "none"}, ""
            
            # Format as an HTML table
            table_header = html.Thead(html.Tr([html.Th(var) for var in bindings[0].keys()]))
            table_rows = []
            for binding in bindings:
                row_cells = []
                for var, value in binding.items():
                    row_cells.append(html.Td(value.get('value', '')))
                table_rows.append(html.Tr(row_cells))
            
            table_body = html.Tbody(table_rows)
            table = dbc.Table([table_header, table_body], bordered=True, hover=True, responsive=True)
            
            # Format results for LLM interpretation
            formatted_results = []
            for binding in bindings:
                result_item = {}
                for var, value in binding.items():
                    result_item[var] = value.get('value', '')
                formatted_results.append(result_item)
            
            results_text = json.dumps(formatted_results, indent=2)
            
            # Send to results-interpreter for interpretation
            try:
                # Get current date for the prompt
                from datetime import datetime
                current_date = datetime.now()
                formatted_date = current_date.strftime("%B %d, %Y")  # e.g., "June 12, 2025"
                iso_date = current_date.strftime("%Y-%m-%d")  # e.g., "2025-06-12"
                
                interpretation_prompt = f"""
                Today's date is {formatted_date}.
                
                I executed a SPARQL query to answer this question: "{original_question or 'unknown question'}"
                
                The query was:
                ```
                {query}
                ```
                
                The results are:
                ```
                {results_text}
                ```
                """
                
                interpretation_response = requests.post(
                    "http://ollama:11434/api/generate",
                    json={
                        "model": "results-interpreter", 
                        "prompt": interpretation_prompt,
                        "stream": False
                    },
                    timeout=45
                )
                
                if interpretation_response.status_code == 200:
                    interpretation = interpretation_response.json().get('response', '').strip()
                    print("Raw interpretation:", interpretation)
                    
                    # Filter out any thinking sections
                    think_parts = interpretation.split("</think>")
                    if len(think_parts) > 1:
                        # Take only what comes after the </think> tag
                        interpretation = think_parts[-1].strip()
                    
                    print("Cleaned interpretation:", interpretation)
                    
                    # Format the interpretation as Markdown
                    interpretation_md = dcc.Markdown(
                        interpretation,
                        dangerously_allow_html=False,
                        className="interpretation-text"
                    )
                    
                    return table, {"display": "block"}, interpretation_md
                else:
                    # If interpretation fails, show just the results
                    return table, {"display": "block"}, "Could not interpret results. The LLM service returned an error."
                    
            except Exception as interp_error:
                # If interpretation fails, show just the results
                return table, {"display": "block"}, f"Could not interpret results: {str(interp_error)}"
                
        else:
            return "Query executed, but no standard results format returned.", {"display": "none"}, ""
            
    except Exception as e:
        return f"Error executing query: {str(e)}", {"display": "none"}, ""

# Callback to update the validation icon
@app.callback(
    Output("query-validation-icon", "children"),
    Input("sparql-query-output", "value"),
    prevent_initial_call=True
)
def update_validation_icon(query):
    if not query:
        return ""
    
    try:
        # Try to execute the query
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        test_results = sparql.query().convert()
        
        # If we get here, the query works!
        return "✓"  # Green checkmark
    except:
        return ""  # No icon if query doesn't work

if __name__ == "__main__":
    import socket
    
    # Get the actual hostname for a friendlier message
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Custom print message
    print(f"Dash app running at:")
    print(f" * Local URL: http://localhost:8050/")
    print(f" * Network URL: http://{local_ip}:8050/ (accessible from other devices)")
    
    # Actually run the app
    app.run_server(host="0.0.0.0", debug=True, use_reloader=False)
