import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, ValidationError
import openai

# Step 1: Configure OpenAI API
openai.api_key = "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" 

# Step 2: Database configuration
# DATABASE_URL = "postgresql+psycopg2://sadmin:sadmin123@localhost:5432/lifestyle-erp"  
DATABASE_URL = "postgresql+psycopg2://postgres:cimxDZDVXtvFhBMSyFVxtzLDNVWyFrTK@monorail.proxy.rlwy.net:57837/railway"  
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Step 3: Define a Pydantic model for validation
class QueryResult(BaseModel):
    data: list

# Step 4: Define a function to query the database
def execute_query(sql_query: str):
    session = Session()
    try:
        result = session.execute(text(sql_query))
        data = [dict(row) for row in result]
        session.commit()
        return QueryResult(data=data).dict()
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

# Step 5: Define a function to convert plain text into SQL
def convert_text_to_sql(plain_text: str):
    prompt = f"""
    You are an assistant that converts plain English queries into SQL statements for a PostgreSQL database.
    Input: "{plain_text}"
    SQL:"""
    response = openai.Completion.create(
        engine="gpt-4o-mini",  
        prompt=prompt,
        max_tokens=150,
        temperature=0
    )
    return response["choices"][0]["text"].strip()

# Step 6: Define the chatbot function
def chatbot(query: str):
    try:
        # Step 6.1: Convert plain text query to SQL
        sql_query = convert_text_to_sql(query)
        print(f"Generated SQL: {sql_query}")  # Debugging SQL
        
        # Step 6.2: Execute SQL query
        result = execute_query(sql_query)
        return result
    except ValidationError as e:
        return {"Validation error": f"Validation error: {e}"}
    except Exception as e:
        return {"Unexpected error": f"Unexpected error: {e}"}

# Step 7: Main program loop
if __name__ == "__main__":
    print("Welcome to the AI Chatbot connected to PostgreSQL. Type 'exit' to quit.")
    while True:
        user_input = input("Ask a question: ")
        if user_input.lower() == "exit":
            break
        response = chatbot(user_input)
        print(response)
