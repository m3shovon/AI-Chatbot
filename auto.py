import psycopg2
import re

# Connection parameters
host = "localhost"
port = "5432"
database = "lifestyle-erp"
user = "sadmin"
password = "sadmin123"

# Read schema from schema.txt
def load_schema(schema_file):
    schema = {}
    current_table = None

    with open(schema_file, "r") as file:
        for line in file:
            line = line.strip()

            # Detect table name
            if line.startswith("Table:"):
                current_table = line.split(":", 1)[1].strip()
                schema[current_table] = []

            # Detect column details
            elif line.startswith("Column:"):
                match = re.search(r"Column: (\w+), Type: (\w+), Nullable: (\w+), Length: (\S+)", line)
                if match:
                    column_name, data_type, is_nullable, length = match.groups()
                    schema[current_table].append({
                        "column_name": column_name,
                        "data_type": data_type,
                        "is_nullable": is_nullable,
                        "length": length
                    })
    return schema

# Execute dynamic queries based on schema
def query_database(schema, query):
    try:
        # Connect to PostgreSQL
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        cursor = connection.cursor()

        # Parse user query
        query = query.lower()

        if "show tables" in query:
            # List all tables
            tables = schema.keys()
            return f"Tables: {', '.join(tables)}"

        elif "select" in query:
            # Match the table name
            match = re.search(r"from (\w+)", query)
            if match:
                table_name = match.group(1)
                if table_name in schema:
                    # Execute the query
                    cursor.execute(query)
                    rows = cursor.fetchall()

                    # Fetch column names
                    col_names = [desc[0] for desc in cursor.description]
                    results = [dict(zip(col_names, row)) for row in rows]
                    return results
                else:
                    return f"Error: Table '{table_name}' does not exist in the schema."
            else:
                return "Error: Invalid query format. Could not find table name."

        elif "describe" in query or "schema" in query:
            # Describe a table
            match = re.search(r"(describe|schema) (\w+)", query)
            if match:
                table_name = match.group(2)
                if table_name in schema:
                    columns = schema[table_name]
                    return columns
                else:
                    return f"Error: Table '{table_name}' does not exist in the schema."
            else:
                return "Error: Invalid query format."

        else:
            return "Error: Unsupported query."

    except Exception as e:
        return f"Error: {e}"

    finally:
        if connection:
            cursor.close()
            connection.close()

# Main function
def main():
    schema_file = "schema.txt"
    schema = load_schema(schema_file)

    print("Database Query Tool (type 'exit' to quit)")
    while True:
        user_query = input("\nEnter your query: ").strip()
        if user_query.lower() == "exit":
            break

        result = query_database(schema, user_query)
        print("\nResult:")
        print(result)

if __name__ == "__main__":
    main()
