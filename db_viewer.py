import pymysql
import sys

# Database connection parameters
db_config = {
    'host': 'mysql-256317f1-viveknikam77789-d41d.k.aivencloud.com',
    'port': 25461,
    'user': 'avnadmin',
    'password': 'AVNS_JdFLlqDAaWDvSMarcTI',
    'database': 'defaultdb',
    'ssl': {'mode': 'REQUIRED'}
}

def connect_to_db():
    try:
        connection = pymysql.connect(**db_config)
        print("Connected to the database!")
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        sys.exit(1)

def show_tables(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print("\nAvailable tables:")
            for table in tables:
                print(f"- {table[0]}")
            
            return [table[0] for table in tables]
    except Exception as e:
        print(f"Error listing tables: {e}")
        return []

def show_table_data(connection, table_name):
    try:
        with connection.cursor() as cursor:
            # Get column names
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            column_names = [column[0] for column in columns]
            
            # Get table data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            print(f"\n== {table_name} ==")
            print("Columns:", ", ".join(column_names))
            print(f"Total rows: {len(rows)}")
            
            if len(rows) > 0:
                print("\nData:")
                for row in rows:
                    formatted_row = [str(cell) for cell in row]
                    print(" | ".join(formatted_row))
    except Exception as e:
        print(f"Error showing table data: {e}")

def main():
    connection = connect_to_db()
    tables = show_tables(connection)
    
    for table in tables:
        show_table_data(connection, table)
    
    connection.close()
    print("\nConnection closed.")

if __name__ == "__main__":
    main() 