import requests
import tiktoken

# Constants for the Groq API
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_TOKEN = "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"  # Replace with your actual Groq API key
MAX_TOKENS = 6000  # Maximum token limit for the model
SCHEMA_FILE = "output.txt"  # File containing the database schema

# Function to load and process the schema
def load_and_summarize_schema(file_path):
    """
    Load the schema file, summarize it if it's too large for token limits, and return the processed schema.
    """
    try:
        with open(file_path, "r") as file:
            schema_lines = file.readlines()
        
        # Summarize the schema into table and column names only
        summarized_schema = []
        for line in schema_lines:
            if line.strip().startswith("CREATE TABLE"):
                summarized_schema.append(line.strip())  # Table name
            elif line.strip() and not line.strip().startswith("("):
                summarized_schema.append(line.strip().split(" ")[0])  # Column name
        
        summarized_schema_text = "\n".join(summarized_schema)
        return summarized_schema_text
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
        return None

# Function to count tokens in a text
def count_tokens(text, model="gpt-4"):
    """
    Count the number of tokens in the provided text using the specified model.
    """
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

# Function to generate SQL from the Groq API
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

# Main function to handle user input and generate SQL queries
def main():
    """
    Main function to load the schema, process user input, and generate SQL queries.
    """
    # Load and summarize the schema
    schema = load_and_summarize_schema(SCHEMA_FILE)
    if not schema:
        print("Failed to load the schema. Exiting.")
        return
    
    print("Schema loaded successfully.")
    
    while True:
        # Get user input for SQL generation
        user_input = input("\nEnter your SQL query request (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        # Generate SQL query
        print("\nGenerating SQL query...")
        sql_query = generate_sql_from_groq(user_input, schema)
        print(f"\nGenerated SQL Query:\n{sql_query}")

# Run the script
if __name__ == "__main__":
    main()
