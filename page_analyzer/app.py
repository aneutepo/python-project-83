from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
import os
import psycopg2
import validators
import requests
from page_analyzer.db_tools import (
    get_connection,
    get_url,
    get_url_check_result,
    get_url_checks,
    insert_check_result_with_id_url,
    insert_url,
    is_url_in_database,
)
from page_analyzer.url_tools import (
    get_domain,
    url_parser,
)


app = Flask(__name__)


load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls')
def get_sites():
    sites = get_url(conn, 'all')
    table = get_url_checks(conn)
    return render_template(
        'show.html',
        sites=sites,
        table=table,
    )


@app.route('/urls', methods=['POST'])
def get_site():
    url_for_check = request.form.to_dict().get('url')
    url_length = len(url_for_check)
    url = get_domain(url_for_check)
    if validators.url(url) and url_length <= 255:
        if is_url_in_database(conn, url):
            flash('Страница уже существует', 'info')
            id = get_url(conn, 'id', url)
        else:
            id = insert_url(conn, url)
            flash('Страница успешно добавлена', 'success')
        return redirect(url_for('get_site_information', id=id))
    else:
        flash('Некорректный URL', 'danger')
        return render_template('index.html', value=url_for_check), 422


@app.route('/urls/<int:id>')
def get_site_information(id):
    data = get_url(conn, 'site', id)
    if data:
        check_result = get_url_check_result(conn, id)
        return render_template(
            'new.html',
            data=data,
            check_result=check_result,
            id=id
        )
    return render_template('nopage.html'), 404


@app.route('/urls/<int:id>/checks', methods=['POST'])
def get_check_site(id):
    url = get_url(conn, 'domain', id)
    try:
        response = requests.get(f'{url}')
        response.raise_for_status()
        status_code, h1, title, description = url_parser(response)
        insert_check_result_with_id_url(conn, id, status_code,
                                        h1, title, description)
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('get_site_information', id=id, ))
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_site_information', id=id, ))


@app.errorhandler(404)
def no_page(error):
    return render_template('nopage.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
