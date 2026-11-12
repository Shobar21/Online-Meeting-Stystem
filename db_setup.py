import sqlite3

# connect to the database file
conn = sqlite3.connect("omms.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE NOT NULL,
password TEXT NOT NULL,
role TEXT NOT NULL
)""")

# Create Meeting table
cursor.execute("""
CREATE TABLE IF NOT EXISTS meetings(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
date TEXT NOT NULL,
time TEXT NOT NULL,
duration TEXT NOT NULL,
agenda TEXT,
host TEXT NOT NULL
)
""")

# Participants
cursor.execute("""
CREATE TABLE IF NOT EXISTS participants (
id INTEGER PRIMARY KEY AUTOINCREMENT,
meeting_id INTEGER NOT NULL,
email TEXT NOT NULL,
status TEXT DEFAULT 'Pending',
FOREIGN KEY (meeting_id) REFERENCES meetings(id)
)
""")
conn.commit()

# Notes for meeting
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes(
id INTEGER PRIMARY KEY AUTOINCREMENT,
meeting_id INTEGER NOT NULL,
content TEXT NOT NULL,
FOREIGN KEY (meeting_id) REFERENCES meetings(id)
)
""")
conn.commit()

# Add test user
testUser = [
("admin", "admin123", "host"),
("john", "john123", "participant"),
("sara", "sara123", "participant"),
("veer", "veer123", "participant"),
("saif", "saif123", "admin"),
]

for user in testUser:
    try:
        cursor.execute("""
INSERT INTO users (username, password, role)
VALUES (?, ?, ?)""", user)
    except sqlite3.IntegrityError:
        print(f"user'{user[0]}' already exist, skipping")
conn.commit()
conn.close()
print("Test users inserted successfully")