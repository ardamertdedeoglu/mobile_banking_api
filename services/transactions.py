import sqlite3

from flask import jsonify, session
from werkzeug.datastructures import MultiDict

from db import make_connection, close_connection


def list_transactions(account_id: int, params: MultiDict[str, str]):
    conn = make_connection()
    if conn is None:
        return jsonify({"error": "cannot connect to database"}), 500

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM accounts WHERE id = ?", (account_id,))

    row = cursor.fetchone()

    if row is None:
        return jsonify({"error": "user or account does not exist"}), 404

    account_user_id = row["user_id"]
    if account_user_id is None:
        return jsonify({"error": "account not found"}), 404

    if session.get("user_id") != account_user_id:
        return jsonify({"error": "cannot list another user's transactions"}), 403

    start_date = params.get("start_date")
    end_date = params.get("end_date")

    if start_date is None and end_date is not None:
        cursor.execute("""
        SELECT account_id, type, amount, counterparty_account_id, created_at
        FROM transactions
        WHERE account_id = ? AND created_at < ?
        ORDER BY created_at DESC;
        """, (account_id, end_date))

    elif start_date is not None and end_date is None:
        cursor.execute("""
        SELECT account_id, type, amount, counterparty_account_id, created_at
        FROM transactions
        WHERE account_id = ? AND created_at > ?
        ORDER BY created_at DESC;
        """, (account_id, start_date))

    elif start_date is not None and end_date is not None:
        cursor.execute("""
        SELECT account_id, type, amount, counterparty_account_id, created_at
        FROM transactions
        WHERE account_id = ? AND created_at > ? AND created_at < ?
        ORDER BY created_at DESC;
        """, (account_id, start_date, end_date))
    else:
        cursor.execute("""
        SELECT account_id, type, amount, counterparty_account_id, created_at
        FROM transactions
        WHERE account_id = ?
        ORDER BY created_at DESC;
        """, (account_id,))

    rows = cursor.fetchall()

    transactions_data = [dict(row) for row in rows]

    close_connection(conn)
    return jsonify(transactions_data), 200

