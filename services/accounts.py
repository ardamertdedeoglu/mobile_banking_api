from typing import Dict

from flask import jsonify, session

from db import make_connection

from datetime import datetime
import sqlite3


def create_account(data: Dict[str, str]):
    account_name = data["name"]
    account_currency = data["currency"]
    account_initial_balance = float(data["initial_balance"])

    if not account_currency or account_currency not in ("USD", "EUR", "TRY"):
        return jsonify({"error": "invalid currency"}), 400

    if not account_initial_balance or account_initial_balance < 0:
        return jsonify({"error": "balance cannot be less than zero"}), 400

    logged_in_user_id = session["user_id"]
    if not logged_in_user_id:
        return jsonify({"error": "cannot create an account without logging in"}), 403

    conn = make_connection()
    if conn is None:
        return jsonify({"error": "database connection failed"}), 500

    cursor = conn.cursor()

    date_string = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    INSERT INTO accounts (user_id, name, currency, balance, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (logged_in_user_id, account_name, account_currency, account_initial_balance, date_string))

    conn.commit()
    return jsonify({"success" : "true", "account_user_id": logged_in_user_id})

def list_accounts():
    conn = make_connection()

    if conn is None:
        return jsonify({"error": "database connection failed"}), 500

    logged_in_user_id = session.get("user_id")
    if not logged_in_user_id:
        return jsonify({"error": "cannot list accounts without logging in"}), 403

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name, currency, balance, created_at FROM accounts
    WHERE user_id = ?
    """, (logged_in_user_id,))

    rows = cursor.fetchall()

    accounts_data = [dict(row) for row in rows]
    return jsonify(accounts_data), 200

