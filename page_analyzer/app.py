from flask import Flask, render_template
from dotenv import load_dotenv
import os


app = Flask(__name__)


load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return "Я живая главная страница"


if __name__ == "__main__":
    app.run(debug=True)
