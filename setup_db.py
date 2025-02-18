import sqlite3

# Connect to SQLite database (it will create database.db if it doesn't exist)
conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Create users table if it doesn't exist
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Commit and close connection
conn.commit()
conn.close()

print("Users table created successfully!")
