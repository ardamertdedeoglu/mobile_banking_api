from typing import Dict
import sqlite3
from flask import jsonify
import bcrypt

from datetime import datetime

from db import make_connection, close_connection


def register(data: Dict[str, str]):
    email = data["email"]
    password = data["password"]

    if email is None or password is None:
        return jsonify({"error": "email and/or password missing"}), 400

    if len(password) < 12:
        return jsonify({"error": "password length must be at least 12."}), 400

    encoded_password = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())

    conn = make_connection()
    if conn is None:
        return jsonify({"error": "database connection failed"}), 500

    # Format the current time into a string
    date_string = datetime.now().strftime("%d.%m.%Y")

    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO users (email, password_hash, created_at)
        VALUES (?, ?, ?)
        """, (email, hashed_password, date_string))
    except sqlite3.IntegrityError:
        return jsonify({"error": "email already exists"}), 400

    conn.commit()

    close_connection(conn)
    return jsonify({"success" : "true", "email" : email, "created_at": date_string}), 201

