from pydantic_ai import Agent
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

# Read schema.txt to validate table names
def get_table_names_from_schema(schema_file="schema.txt"):
    with open(schema_file, "r") as file:
        lines = file.readlines()

    table_names = []
    for line in lines:
        if line.startswith("Table:"):
            table_names.append(line.split(":")[1].strip())
    return table_names

# Database connection setup
def connect_to_db():
    return psycopg2.connect(
        dbname="lifestyle-erp",
        user="sadmin",
        password="sadmin123",
        host="localhost",
        port="5432"
    )

# Define the database query result structure
class DatabaseQueryResult(BaseModel):
    data: dict
    message: str

# Initialize the agent
db_agent = Agent(
    "groq:llama3-70b-8192",
    result_type=DatabaseQueryResult,
    system_prompt="Your helpful database assistant"
)

# Define the database query tool
@db_agent.tool_plain
def query_database(query: str):
    try:
        # Extract the table name from the query
        table_names = get_table_names_from_schema()
        table_name = next((name for name in table_names if name in query), None)

        if not table_name:
            return {"data": {}, "message": "Error: No valid table name found in the query."}

        # Connect to the database
        conn = connect_to_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Execute the query
        cursor.execute(query)
        result = cursor.fetchall()

        # Close the connection
        cursor.close()
        conn.close()

        return {"data": result, "message": "Query executed successfully!"}
    except Exception as e:
        return {"data": {}, "message": f"An error occurred: {str(e)}"}

# Run the agent
query = input("Enter your query: ")
result = db_agent.run_sync(query)
print(f"Message: {result.data.message}")
print(f"Data: {result.data.data}")
