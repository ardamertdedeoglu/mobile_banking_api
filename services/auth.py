import os
from typing import Dict
import sqlite3
from flask import jsonify, session
import bcrypt

from datetime import datetime

from db import make_connection, close_connection

def register(data: Dict[str, str]):
    email = data.get("email")
    password = data.get("password")

    if email is None or password is None:
        return jsonify({"error": "email and/or password missing"}), 400

    if len(password) < 12:
        return jsonify({"error": "password length must be at least 12."}), 400

    encoded_password = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())

    conn = make_connection()
    if conn is None:
        return jsonify({"error": "database connection failed"}), 500

    date_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO users (email, password_hash, created_at)
        VALUES (?, ?, ?)
        """, (email, hashed_password, date_string))
    except sqlite3.IntegrityError:
        return jsonify({"error": "email already exists"}), 409

    conn.commit()

    close_connection(conn)
    return jsonify({"success" : "true", "email" : email, "created_at": date_string}), 201

def login(data: Dict[str, str]):
    email = data.get("email")
    password = data.get("password")
    if email is None or password is None:
        return jsonify({"error": "email and/or password missing"}), 400

    conn = make_connection()
    if conn is None:
        return jsonify({"error": "database connection failed"}), 500

    cursor = conn.cursor()
    encoded_password = password.encode("utf-8")
    cursor.execute("""
    SELECT id, password_hash FROM users
    WHERE email = ?
    """, (email,))

    row = cursor.fetchone()
    if row is None:
        return jsonify({"error": "an account with given email is not found"}), 404

    close_connection(conn)
    if bcrypt.checkpw(encoded_password, row[1]):
        user_id = row[0]
        session["user_id"] = user_id
        return jsonify({"success": "true", "session": session["user_id"]}), 200
    else:
        return jsonify({"error": "invalid email or password"}), 401



def logout():
    if "user_id" not in session:
        return jsonify({"error": "user not logged in"}), 401
    session.pop("user_id", None)
    return jsonify({"success": "true", "message": "You've been logged out successfully."}), 200



