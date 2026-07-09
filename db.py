import sqlite3

def make_connection():
    try:
        connection = sqlite3.connect('bank.db')
    except sqlite3.OperationalError:
        print('Database does not exist')
        return None

    return connection

def close_connection(conn: sqlite3.Connection):
    conn.close()