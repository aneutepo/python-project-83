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


class URLCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('url.id'), nullable=False)
    status_code = db.Column(db.Integer, nullable=True)
    h1 = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


# Связь между таблицами
URL.checks = db.relationship('URLCheck', backref='url', lazy=True)


# Главная страница с формой ввода
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()

        # Валидация URL
        if not url:
            flash("URL не может быть пустым.")
            return redirect(url_for('index'))

        if len(url) > 255:
            flash("URL не должен превышать 255 символов.")
            return redirect(url_for('index'))

        if not url.startswith(('http://', 'https://')):
            flash("Неверный формат URL. Используйте http:// или https://.")
            return redirect(url_for('index'))

        # Проверяем, есть ли уже такой URL
        existing_url = URL.query.filter_by(name=url).first()
        if existing_url:
            flash("Этот URL уже добавлен.")
            return redirect(url_for('list_urls'))

        # Добавление в БД
        new_url = URL(name=url)
        db.session.add(new_url)
        db.session.commit()

        flash("URL успешно добавлен.")
        return redirect(url_for('list_urls'))  # После добавления перенаправляем

    return render_template('index.html')  # Рендерим главную


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


# Создание новой проверки
@app.route('/urls/<int:id>/checks', methods=['POST'])
def create_check(id):
    url = URL.query.get_or_404(id)

    # Создаем новую запись в таблице проверок
    new_check = URLCheck(url_id=url.id)
    db.session.add(new_check)
    db.session.commit()

    flash("Проверка успешно добавлена.")
    return redirect(url_for('view_url', id=id))


if __name__ == "__main__":
    with app.app_context():  # Создание контекста приложения
        db.create_all()  # Создание всех таблиц в базе данных
    app.run(debug=True)
