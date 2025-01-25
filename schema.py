import psycopg2
from psycopg2 import sql


def get_database_schema(connection_params):
    """
    Connects to a PostgreSQL database and retrieves the full schema.
    
    Parameters:
        connection_params (dict): Database connection details.
        
    Returns:
        dict: A dictionary representation of the database schema.
    """
    try:
        # Connect to the PostgreSQL database
        with psycopg2.connect(**connection_params) as conn:
            with conn.cursor() as cur:
                # Fetch all schemas
                cur.execute("SELECT schema_name FROM information_schema.schemata")
                schemas = [row[0] for row in cur.fetchall()]

                database_schema = {}

                for schema in schemas:
                    # Fetch all tables in the schema
                    cur.execute(
                        sql.SQL(
                            """
                            SELECT table_name 
                            FROM information_schema.tables
                            WHERE table_schema = %s
                            """
                        ),
                        [schema],
                    )
                    tables = [row[0] for row in cur.fetchall()]

                    database_schema[schema] = {}

                    for table in tables:
                        # Fetch columns and their details
                        cur.execute(
                            sql.SQL(
                                """
                                SELECT column_name, data_type, is_nullable
                                FROM information_schema.columns
                                WHERE table_schema = %s AND table_name = %s
                                """
                            ),
                            [schema, table],
                        )
                        columns = [
                            {"name": row[0], "type": row[1], "nullable": row[2]}
                            for row in cur.fetchall()
                        ]

                        # Fetch constraints
                        cur.execute(
                            sql.SQL(
                                """
                                SELECT constraint_type, constraint_name
                                FROM information_schema.table_constraints
                                WHERE table_schema = %s AND table_name = %s
                                """
                            ),
                            [schema, table],
                        )
                        constraints = [
                            {"type": row[0], "name": row[1]} for row in cur.fetchall()
                        ]

                        # Store table details
                        database_schema[schema][table] = {
                            "columns": columns,
                            "constraints": constraints,
                        }

                return database_schema

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None


# Connection parameters for the database
connection_params = {
    "dbname": "lifestyle-erp",
    "user": "sadmin",
    "password": "sadmin123",
    "host": "localhost", 
    "port": "5432",  
}

# Fetch and print the schema
if __name__ == "__main__":
    schema = get_database_schema(connection_params)
    if schema:
        import json

        print(json.dumps(schema, indent=4))
