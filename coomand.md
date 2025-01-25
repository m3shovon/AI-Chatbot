python schema2.py > output.txt


Give me Chartofaccount table accountcode of Cash 

give me all the invoice number for last 3 months

def generate_sql_from_groq(user_input, schema):
    """
    Generate an SQL query from the provided schema and user input using the Groq API.
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Build the prompt with schema and user query
    prompt = f"You are an expert SQL assistant. Analyze the following database schema and generate SQL queries based on it:\n\n{schema}\n\nQuery: {user_input}"
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are an SQL assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        sql_query = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        if sql_query.lower().startswith("select"):
            return sql_query
        else:
            return "Error: No valid SQL query found in the response."
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Groq API: {e}"