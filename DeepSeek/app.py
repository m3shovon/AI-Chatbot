import deepseek  # Import the deepseek module
from transformers import pipeline, GPT2Tokenizer

# Initialize the chatbot model
chatbot = pipeline('text-generation', model='distilgpt2')

# Initialize the tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")

# Function to truncate the input prompt to fit within the model's token limit
def truncate_prompt(prompt: str, max_tokens: int = 500) -> str:
    tokens = tokenizer.encode(prompt, truncation=True, max_length=max_tokens)
    return tokenizer.decode(tokens, skip_special_tokens=True)

# Function to generate a response using the chatbot model
def generate_response(prompt: str) -> str:
    truncated_prompt = truncate_prompt(prompt, max_tokens=500)  # Truncate the prompt
    response = chatbot(truncated_prompt, max_new_tokens=100)[0]['generated_text']
    return response

# Function to handle user queries
def handle_query(query: str, table_schemas: dict) -> str:
    # Check if the query is related to the database schema
    if "tables" in query.lower() or "table" in query.lower():
        # Extract table names from the schema
        table_names = list(table_schemas.keys())
        return f"The database contains the following tables: {', '.join(table_names)}."
    elif "schema" in query.lower():
        # Generate a response based on the schema
        prompt = f"The user asked: {query}. Here is the database schema: {table_schemas}"
        return generate_response(prompt)
    else:
        # Generate a generic response for non-schema-related queries
        return generate_response(query)

# Main function to run the chatbot
def main():
    # Load the database schema and Pydantic models from deepseek.py
    conn = deepseek.get_db_connection()
    table_names = deepseek.fetch_table_names(conn)
    table_schemas = {}
    for table_name in table_names:
        schema = deepseek.fetch_table_schema(conn, table_name)
        table_schemas[table_name] = schema

    print("Chatbot is ready! Type 'exit' to quit.")

    while True:
        # Get user input
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye!")
            break

        # Handle the user query
        response = handle_query(user_input, table_schemas)
        print(f"Chatbot: {response}")

    conn.close()

if __name__ == "__main__":
    main()