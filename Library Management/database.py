import sqlite3

def get_db():
    conn = sqlite3.connect("library.db")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        name TEXT,
        author TEXT,
        serial_no TEXT UNIQUE,
        is_issued INTEGER DEFAULT 0
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS memberships (
        id INTEGER PRIMARY KEY,
        member_name TEXT,
        duration TEXT,
        expiry_date TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY,
        book_id INTEGER,
        user_id INTEGER,
        issue_date TEXT,
        return_date TEXT,
        remarks TEXT,
        fine INTEGER DEFAULT 0,
        fine_paid INTEGER DEFAULT 0
    )""")

    conn.commit()
    conn.close()

init_db()
