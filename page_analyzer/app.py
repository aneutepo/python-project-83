from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Инициализируем приложение Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://anton:admin@localhost:5432/page_analyzer_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

# Инициализируем SQLAlchemy
db = SQLAlchemy(app)

# Модель для таблицы URLs
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Главная страница с формой ввода
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_url():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()

        # Валидация URL
        if not url:
            flash("URL не может быть пустым.")
            return redirect(url_for('add_url'))

        if len(url) > 255:
            flash("URL не должен превышать 255 символов.")
            return redirect(url_for('add_url'))

        if not url.startswith(('http://', 'https://')):
            flash("Неверный формат URL. Используйте http:// или https://.")
            return redirect(url_for('add_url'))

        # Добавление в БД
        new_url = URL(name=url)
        db.session.add(new_url)
        db.session.commit()

        flash("URL успешно добавлен.")
        return redirect(url_for('list_urls'))  # После добавления кидаем на список

    return render_template('add.html')  # Если `GET`, рендерим страницу с формой





# Страница с информацией об отдельном URL
@app.route('/urls/<int:id>')
def view_url(id):
    url = URL.query.get_or_404(id)
    return render_template('view_url.html', url=url)

# Страница с выводом всех URL
@app.route('/urls')
def list_urls():
    urls = URL.query.order_by(URL.created_at.desc()).all()
    return render_template('list_urls.html', urls=urls)

if __name__ == "__main__":
    with app.app_context():  # Создание контекста приложения
        db.create_all()  # Создание всех таблиц в базе данных
    app.run(debug=True)
