import psycopg2

# Connection parameters
host = "localhost"
port = "5432"
database = "lifestyle-erp"
user = "sadmin"
password = "sadmin123"

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

    # Fetch table schema details
    cursor.execute("""
        SELECT table_name, column_name, data_type, is_nullable, character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """)
    columns = cursor.fetchall()

    print("Database Schema:")
    current_table = None
    for column in columns:
        table_name, column_name, data_type, is_nullable, char_length = column

        # Print table name once
        if table_name != current_table:
            print(f"\nTable: {table_name}")
            print("-" * 30)
            current_table = table_name

        # Print column details
        nullable = "YES" if is_nullable == "YES" else "NO"
        print(f"Column: {column_name}, Type: {data_type}, Nullable: {nullable}, Length: {char_length or 'N/A'}")

    # Fetch primary keys
    cursor.execute("""
        SELECT tc.table_name, kcu.column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_schema = 'public';
    """)
    primary_keys = cursor.fetchall()

    print("\nPrimary Keys:")
    for pk in primary_keys:
        print(f"Table: {pk[0]}, Column: {pk[1]}")

except Exception as e:
    print(f"Error: {e}")
finally:
    if connection:
        cursor.close()
        connection.close()