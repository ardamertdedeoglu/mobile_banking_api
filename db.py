import sqlite3


def make_connection():
    try:
        connection = sqlite3.connect('bank.db')
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS "users" (
            "id"	INTEGER,
            "email"	TEXT NOT NULL UNIQUE,
            "password_hash"	TEXT NOT NULL,
            "created_at"	TEXT NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS "accounts" (
            "id"	INTEGER NOT NULL,
            "user_id"	INTEGER NOT NULL,
            "name"	TEXT NOT NULL,
            "currency"	TEXT DEFAULT 'TRY',
            "balance"	REAL DEFAULT 0,
            "created_at"	TEXT,
            PRIMARY KEY("id" AUTOINCREMENT),
            FOREIGN KEY("user_id") REFERENCES "users"("id")
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS "transactions" (
            "id"	INTEGER NOT NULL,
            "account_id"	INTEGER NOT NULL,
            "type"	TEXT NOT NULL,
            "amount"	REAL NOT NULL,
            "counterparty_account_id"	INTEGER,
            "created_at"	TEXT NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT),
            FOREIGN KEY("account_id") REFERENCES "accounts"("id")
        );
        """)


        connection.commit()
    except sqlite3.Error:
        return None

    return connection


def close_connection(conn: sqlite3.Connection):
    conn.close()
