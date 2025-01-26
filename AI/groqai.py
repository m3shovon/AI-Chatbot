import psycopg2
import requests

# Database connection parameters
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "lifestyle-erp",
    "user": "sadmin",
    "password": "sadmin123",
}

# Groq API configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"  
GROQ_API_TOKEN = "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"  

# Read schema from a saved file
def load_schema(file_path="output.txt", relevant_table="invoice"):
    try:
        with open(file_path, "r") as file:
            schema_lines = file.readlines()
            # Extract only relevant table schema
            relevant_schema = []
            capture = False
            for line in schema_lines:
                if relevant_table in line:
                    capture = True
                if capture:
                    relevant_schema.append(line)
                if line.strip() == "":
                    capture = False  
            return "".join(relevant_schema)
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
        return None

# def load_schema(file_path="output.txt"):
#     try:
#         with open(file_path, "r") as file:
#             schema_lines = file.readlines()
#             summarized_schema = []
#             for line in schema_lines:
#                 if line.strip().startswith("CREATE TABLE"):
#                     summarized_schema.append(line.strip())
#                 elif line.strip().startswith("(") or line.strip().startswith(");"):
#                     continue  # Skip column definitions
#                 elif line.strip():
#                     summarized_schema.append(line.strip().split(" ")[0])  # Only column name
#             return "\n".join(summarized_schema)
#     except FileNotFoundError:
#         print(f"Error: The file {file_path} does not exist.")
#         return None

# Generate SQL query using Groq API
def generate_sql_from_groq(user_input, schema):
    headers = {
        "Authorization": f"Bearer {GROQ_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": f"You are an expert SQL assistant. Analyze the database schema below and generate SQL queries based on it. Always return only valid SQL queries. Do not return explanations.\n\nDatabase schema:\n{schema}"
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        response.raise_for_status()

        data = response.json()
        # Extract SQL query from response
        sql_query = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        if sql_query.lower().startswith("select"):
            return sql_query
        else:
            return "Error: No valid SQL query found in the response."

    except requests.exceptions.RequestException as e:
        return f"Error communicating with Groq API: {e}"

# Execute the SQL query against the database
def fetch_data_from_db(query):
    try:
        if query.startswith("Error:"):
            return query  # Return the error message directly
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except Exception as e:
        return f"Error executing query: {e}"

# Chat interface for user interaction
def chat_interface(schema):
    if not schema:
        print("Error: No schema loaded. Exiting.")
        return

    print("ChatGPT Database Assistant (Groq API Edition)")
    print("Type your query to fetch data from the database. Type 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Generate SQL query using Groq API
        sql_query = generate_sql_from_groq(user_input, schema)
        print(f"Generated SQL Query: {sql_query}")

        # Fetch and display data
        results = fetch_data_from_db(sql_query)
        print("\nQuery Results:")
        if isinstance(results, list) and results:
            for row in results:
                print(row)
        elif results:
            print(results)
        else:
            print("No results found.")

# Main function
if __name__ == "__main__":
    schema = load_schema()
    chat_interface(schema)
