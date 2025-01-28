import os
from sqlalchemy import create_engine, inspect
from pydantic import BaseModel, Field
import openai

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "lifestyle-erp",
    "user": "sadmin",
    "password": "sadmin123",
}

# OpenAI API Key (replace with your actual API key)
openai.api_key = "your_openai_api_key"

# Database connection URL
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Connect to the PostgreSQL database
engine = create_engine(DATABASE_URL)

def fetch_database_schema():
    """Fetch the database schema and tables."""
    inspector = inspect(engine)
    schema = {}
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema[table_name] = [{"name": col["name"], "type": col["type"]} for col in columns]
    return schema

def generate_pydantic_models(schema):
    """Generate Pydantic models from the schema."""
    models = {}
    for table, columns in schema.items():
        # Create a dictionary of fields with proper type annotations
        fields = {
            col["name"]: (str, Field(..., description=f"Type: {col['type']}"))
            for col in columns
        }
        # Dynamically create the model class
        model = type(
            table.capitalize(),  # Class name
            (BaseModel,),        # Base class
            {"__annotations__": {k: v[0] for k, v in fields.items()}, **fields},
        )
        models[table] = model
    return models

def train_with_ai(schema):
    """Send schema to the AI model for training."""
    # Prepare schema description
    schema_description = "Database Schema:\n" + "\n".join(
        f"Table {table}: {', '.join([col['name'] + ' (' + str(col['type']) + ')' for col in columns])}"
        for table, columns in schema.items()
    )

    try:
        response = openai.completions.create(
            model="gpt-3.5-turbo",  # Correct OpenAI Chat Model
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that analyzes database schemas and provides insights or suggestions.",
                },
                {
                    "role": "user",
                    "content": f"Given the following database schema, generate insights or suggestions:\n\n{schema_description}",
                },
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"]
    except openai.OpenAIError as e:
        return f"Error with OpenAI API: {e}"

# Main execution
if __name__ == "__main__":
    print("Connecting to the database...")
    try:
        schema = fetch_database_schema()
        print("Database schema fetched successfully.")

        print("\nGenerating Pydantic models...")
        models = generate_pydantic_models(schema)
        for table, model in models.items():
            print(f"\nPydantic Model for Table {table}:\n{model.schema_json(indent=2)}")

        print("\nTraining with AI...")
        ai_response = train_with_ai(schema)
        print("\nAI Response:")
        print(ai_response)
    except Exception as e:
        print(f"Error: {e}")
