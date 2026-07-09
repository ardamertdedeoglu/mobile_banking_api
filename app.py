from flask import Flask, request
from services.auth import register
app = Flask(__name__)


@app.post("/api/auth/register")
def handle_register():
    data = request.get_json() or {}
    return register(data)

if __name__ == '__main__':
    app.run(debug=True)