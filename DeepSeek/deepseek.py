import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, create_model
from typing import Dict, Type
from transformers import pipeline, GPT2Tokenizer

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "lifestyle-erp",
    "user": "sadmin",
    "password": "sadmin123",
}

# Function to connect to the database
def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# Function to fetch all table names
def fetch_table_names(conn):
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

# Function to fetch schema for a specific table
def fetch_table_schema(conn, table_name):
    query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s;
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (table_name,))
        return {row[0]: row[1] for row in cursor.fetchall()}

# Function to dynamically create Pydantic models
def create_pydantic_models(table_schemas: Dict[str, Dict[str, str]]) -> Dict[str, Type[BaseModel]]:
    models = {}
    for table_name, columns in table_schemas.items():
        fields = {col: (map_data_type(dtype), ...) for col, dtype in columns.items()}
        models[table_name] = create_model(table_name, **fields)
    return models

# Helper function to map PostgreSQL data types to Python types
def map_data_type(data_type: str):
    type_mapping = {
        "integer": int,
        "bigint": int,
        "smallint": int,
        "text": str,
        "varchar": str,
        "char": str,
        "boolean": bool,
        "date": str,
        "timestamp": str,
        "numeric": float,
        "real": float,
        "double precision": float,
    }
    return type_mapping.get(data_type, str)  # Default to str if type is not found

# Function to truncate the input prompt to fit within the model's token limit
def truncate_prompt(prompt: str, max_tokens: int = 500) -> str:
    tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
    tokens = tokenizer.encode(prompt, truncation=True, max_length=max_tokens)
    return tokenizer.decode(tokens, skip_special_tokens=True)

# Function to generate a description using an AI model
def generate_description(schema):
    generator = pipeline('text-generation', model='distilgpt2')
    prompt = f"Generate a description for the following database schema: {schema}"
    truncated_prompt = truncate_prompt(prompt, max_tokens=500)  # Truncate the prompt
    return generator(truncated_prompt, max_new_tokens=100)[0]['generated_text']

# Main function
def main():
    conn = get_db_connection()

    # Fetch all table names
    table_names = fetch_table_names(conn)
    print("Tables in the database:", table_names)

    # Fetch schema for each table
    table_schemas = {}
    for table_name in table_names:
        schema = fetch_table_schema(conn, table_name)
        table_schemas[table_name] = schema
        print(f"Schema for table '{table_name}':", schema)

    # Dynamically create Pydantic models
    pydantic_models = create_pydantic_models(table_schemas)
    print("Generated Pydantic models:", pydantic_models)

    # Generate a description using the AI model
    description = generate_description(table_schemas)
    print("Generated Description:", description)

    conn.close()

if __name__ == "__main__":
    main()