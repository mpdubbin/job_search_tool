import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect("data/sqlite/database.db")

# Read the table into a pandas DataFrame
df = pd.read_sql_query("SELECT * FROM jobs;", conn)

# # Delete rows
# cursor = conn.cursor()
# cursor.execute("DELETE FROM jobs WHERE company_name LIKE 'Stripe';")
# conn.commit()        
# df = pd.read_sql_query("SELECT * FROM jobs;", conn)  

# Close the connection
conn.close()

# Print or use the DataFrame
print(df)
