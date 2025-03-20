import sqlite3
import json

def insert_json_into_db(json_data: dict, db_name: str = "data/sqlite/database.db", table_name: str = "jobs") -> None:
    """
    Inserts a JSON object as a row into an SQLite database table.
    """
    # Connect to SQLite
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Extract columns and values from JSON
    columns = ', '.join(json_data.keys())
    placeholders = ', '.join(['?'] * len(json_data))
    values = tuple(json_data.values())

    # SQL Query for inserting data
    sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

    # Execute query
    cursor.execute(sql_query, values)

    # Commit and close connection
    conn.commit()
    conn.close()