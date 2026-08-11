from flask import Flask
from api import register_routes

app = Flask(__name__)

register_routes(app)

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False,
        threaded=True
    )