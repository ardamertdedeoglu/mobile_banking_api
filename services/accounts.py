from typing import Dict

from flask import jsonify, session

from db import make_connection, close_connection

from datetime import datetime
import sqlite3


def create_account(data: Dict[str, str]):
    account_name = data.get("name")
    account_currency = data.get("currency")

    account_initial_balance = data.get("initial_balance")

    if account_initial_balance is None:
        return jsonify({"error": "balance must be a number"}), 400

    account_initial_balance = float(account_initial_balance)

    if not account_currency or account_currency not in ("USD", "EUR", "TRY"):
        return jsonify({"error": "invalid currency"}), 400

    if account_initial_balance < 0:
        return jsonify({"error": "balance cannot be negative"}), 400

    logged_in_user_id = session["user_id"]

    conn = make_connection()
    if conn is None:
        return jsonify({"error": "database connection failed"}), 500

    cursor = conn.cursor()

    date_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO accounts (user_id, name, currency, balance, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (logged_in_user_id, account_name, account_currency, account_initial_balance, date_string))

    conn.commit()
    close_connection(conn)
    return jsonify({"success" : "true", "account_user_id": logged_in_user_id}), 201

def list_accounts():
    conn = make_connection()

    if conn is None:
        return jsonify({"error": "database connection failed"}), 500

    logged_in_user_id = session.get("user_id")

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name, currency, balance, created_at FROM accounts
    WHERE user_id = ?
    """, (logged_in_user_id,))

    rows = cursor.fetchall()

    accounts_data = [dict(row) for row in rows]
    close_connection(conn)
    return jsonify(accounts_data), 200

def list_accounts_by_id(account_id):
    conn = make_connection()
    if conn is None:
        return jsonify({"error": "database connection failed"}), 500

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
    SELECT user_id, name, currency, balance, created_at FROM accounts
    WHERE id = ?
    """, (account_id,))

    row = cursor.fetchone()
    if row is None:
        return jsonify({"error": "account not found"}), 404

    account_user_id = row["user_id"]
    if account_user_id != session.get("user_id"):
        return jsonify({"error": "cannot see another user's account"}), 403

    close_connection(conn)
    return jsonify(dict(row)), 200


