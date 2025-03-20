import pandas as pd
import sqlite3

db_name = "data/sqlite/database.db" 
table_name = "jobs"

csv_file = pd.read_csv("data/sqlite/initial_job_table.csv")

# Connect to SQLite
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Define the table schema
cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        company_name TEXT,
        job_title TEXT,
        website TEXT,
        salary_floor INTEGER,
        salary_ceiling INTEGER,
        office_status TEXT,
        location TEXT,
        application_status TEXT
    );
""")

csv_file.to_sql(table_name, conn, if_exists="replace", index=False)

conn.commit()
conn.close()