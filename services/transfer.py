import sqlite3
from typing import Dict

from flask import jsonify, session

from db import make_connection, close_connection
from datetime import datetime


def make_transfer(data: Dict[str, str]):
    from_account = data.get("from_account")
    to_account = data.get("to_account")

    if from_account is None or to_account is None:
        return jsonify({"error": "from_account and to_account are required"}), 400

    from_account = int(from_account)

    conn = make_connection()
    if conn is None:
        return jsonify({"error": "database connection failed"}), 500

    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_id, balance FROM accounts
    WHERE id = ?
    """, (from_account,))
    row = cursor.fetchone()
    if row is None:
        return jsonify({"error": "account cannot be found"}), 404

    from_account_user_id = row[0]
    available_balance = row[1]

    logged_in_user_id = session.get("user_id")

    if logged_in_user_id != from_account_user_id:
        return jsonify({"error": "invalid sender account"}), 400

    amount = data.get("amount")
    if amount is None:
        return jsonify({"error": "amount is required"}), 400

    amount = float(amount)
    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400

    if available_balance < amount:
        return jsonify({"error": "balance cannot be less than amount"}), 400

    date_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute("BEGIN")
        if to_account == "":
            transfer_type = 'deposit'
            available_balance += amount
            cursor.execute("""
            INSERT INTO transactions (account_id, type, amount, counterparty_account_id, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (from_account, transfer_type, amount, None, date_string))

            cursor.execute("""
            UPDATE accounts
            SET balance = ?
            WHERE id = ?
            """, (available_balance, from_account))
        else:
            to_account = int(to_account)
            if to_account == from_account:
                conn.rollback()
                return jsonify({"error": "you cannot use the same account for transfer"}), 409
            else:
                transfer_type = "transfer"
                cursor.execute("""
                SELECT balance FROM accounts
                WHERE id = ?
                """, (to_account,))

                row = cursor.fetchone()
                if row is None:
                    conn.rollback()
                    return jsonify({"error": "invalid receiver account"}), 400

                to_account_balance = row[0]

                available_balance -= amount
                to_account_balance += amount

                cursor.executemany("""
                INSERT INTO transactions (account_id, type, amount, counterparty_account_id, created_at)
                VALUES
                    (?, ?, ?, ?, ?)
                """, [(to_account, 'transfer_in', amount, from_account, date_string),
                      (from_account, 'transfer_out', amount, to_account, date_string)])

                cursor.execute("""
                UPDATE accounts
                SET balance = ?
                WHERE id = ?
                """, (available_balance, from_account))

                cursor.execute("""
                UPDATE accounts
                SET balance = ?
                WHERE id = ?
                """, (to_account_balance, to_account))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    close_connection(conn)
    if transfer_type == 'deposit':
        return jsonify(
            {"success": "true", "type": transfer_type, "sender_balance": available_balance}), 201
    else:
        return jsonify({"success": "true", "sender_balance": available_balance, "receiver_balance": to_account_balance}), 201
