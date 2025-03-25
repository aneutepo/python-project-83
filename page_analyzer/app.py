import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()


app = Flask(__name__)

app.config['d4f5c9b1e2a3ed4567f8c9a1d1b2345d'] = os.getenv('d4f5c9b1e2a3ed4567f8c9a1d1b2345d')


@app.route("/")
def index():
    return "Hello, Flask!"


if __name__ == "__main__":
    app.run(debug=True)
