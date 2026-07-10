import os

from flask import Flask, request, session, redirect, url_for, jsonify
from dotenv import load_dotenv

from services.auth import register, login, logout
from services.accounts import create_account, list_accounts
app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

@app.post("/api/auth/register")
def handle_register():
    data = request.get_json() or {}
    return register(data)

@app.route("/api/auth/login", methods=['POST', 'GET'])
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
@app.get("/api/accounts/<int:user_id>")
def list_accounts_by_id(user_id):
    if session.get('user_id') != user_id:
        return jsonify({"error": "cannot list another users accounts"}), 403

    return list_accounts()

@app.get("/logout")
def handle_logout():
    return logout()

if __name__ == '__main__':
    app.run(debug=True)