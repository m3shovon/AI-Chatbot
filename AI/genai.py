import psycopg2
import openai

# GPT Model setup
openai.api_key = "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"  

# PostgreSQL connection parameters
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "lifestyle-erp",
    "user": "sadmin",
    "password": "sadmin123",
}

# Read schema from the saved file
def load_schema(file_path="output.txt"):
    with open(file_path, "r") as file:
        return file.read()

# Function to fetch data from the database
def fetch_data_from_db(query):
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except Exception as e:
        return f"Error executing query: {e}"

# Chat interface for dynamic queries
def chat_interface(schema):
    print("ChatGPT Database Assistant")
    print("Type your query to fetch data from the database. Type 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Use GPT to process the user query and generate an SQL query
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # Change model as needed
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant. Here is the database schema:\n{schema}"},
                    {"role": "user", "content": f"Generate an SQL query for: {user_input}"}
                ],
                max_tokens=200,
                temperature=0.7
            )

            # Extract SQL query from GPT response
            sql_query = response["choices"][0]["message"]["content"].strip()
            print(f"Generated SQL Query: {sql_query}")

            # Fetch data from the database
            results = fetch_data_from_db(sql_query)

            # Display results
            print("\nQuery Results:")
            if isinstance(results, list) and results:
                for row in results:
                    print(row)
            elif results:
                print(results)
            else:
                print("No results found.")

        except Exception as e:
            print(f"Error: {e}")

# Main function
if __name__ == "__main__":
    schema = load_schema()
    chat_interface(schema)
