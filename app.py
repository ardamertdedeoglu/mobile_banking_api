import os

from flask import Flask, request
from dotenv import load_dotenv

from services.auth import register, login
app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)