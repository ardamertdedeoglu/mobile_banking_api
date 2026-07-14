import os

from flask import Flask, request, session, redirect, url_for, jsonify, render_template
from dotenv import load_dotenv

from db import initialize_db
from services.auth import register, login, logout
from services.accounts import create_account, list_accounts, list_accounts_by_id
from services.transfer import make_transfer
from services.transactions import list_transactions
app = Flask(__name__)
initialize_db()

@app.get("/")
def index():
    return render_template("index.html")

load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

@app.post("/api/auth/register")
def handle_register():
    data = request.get_json() or {}
    return register(data)

@app.post("/api/auth/login")
def handle_login():
    data = request.get_json() or {}
    return login(data)

@app.route("/api/accounts", methods=['POST', 'GET'])
def handle_account_system():
    if 'user_id' in session:
        if request.method == 'GET':
            return list_accounts()
        elif request.method == 'POST':
            data = request.get_json() or {}
            return create_account(data)
        return jsonify({"error": "invalid method"}), 400
    else:
        return jsonify({"error": "login required"}), 401

@app.get("/api/accounts/<int:account_id>")
def handle_list_accounts_by_id(account_id):
    if "user_id" not in session:
        return jsonify({"error": "cannot list accounts without logging in"}), 401
    return list_accounts_by_id(account_id)

@app.post("/api/transfers")
def handle_transfer():
    if "user_id" not in session:
        return jsonify({"error": "cannot make transfer without logging in"}), 401
    data = request.get_json() or {}
    return make_transfer(data)

@app.get("/api/accounts/<int:account_id>/transactions")
def handle_transactions(account_id):
    if 'user_id' not in session:
        return jsonify({"error": "cannot list transactions without logging in"}), 401
    return list_transactions(account_id, request.args)
@app.get("/logout")
def handle_logout():
    return logout()

if __name__ == '__main__':
    app.run(debug=True)