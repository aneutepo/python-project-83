import psycopg2
from psycopg2.extras import NamedTupleCursor


def get_connection(db_url):
    connection = psycopg2.connect(db_url)
    return connection


def insert_url(connection, name):
    with connection as con:
        with con.cursor(cursor_factory=NamedTupleCursor) as curs:
            sql_name = """INSERT INTO public.urls (name)
                          VALUES (%s) RETURNING id;"""
            curs.execute(sql_name, (name,))
            result = curs.fetchone()
            return result.id


def get_url(connection, action, value=None):
    with connection as con:
        with con.cursor(cursor_factory=NamedTupleCursor) as curs:
            if action == 'all':
                sql_select = "SELECT * FROM public.urls ORDER BY id DESC;"
                curs.execute(sql_select)
                result = curs.fetchall()
                return result
            elif action == 'site':
                _id = value
                sql_id = "SELECT * FROM public.urls WHERE id = %s;"
                curs.execute(sql_id, (_id,))
                result = curs.fetchone()
                return result
            elif action == 'id':
                url = value
                sql_url = "SELECT id FROM public.urls WHERE name = %s;"
                curs.execute(sql_url, (url,))
                result = curs.fetchone()
                return result.id
            elif action == 'domain':
                _id = value
                sql_id = "SELECT name FROM public.urls WHERE id = %s;"
                curs.execute(sql_id, (_id,))
                result = curs.fetchone()
                return result.name


def get_url_check_result(connection, _id):
    with connection as con:
        with con.cursor(cursor_factory=NamedTupleCursor) as curs:
            sql_id = """SELECT * FROM public.url_checks
                          WHERE id = %s ORDER BY url_id DESC;"""
            curs.execute(sql_id, (_id,))
            result = curs.fetchall()
            return result


def get_url_checks(connection):
    with connection as con:
        with con.cursor(cursor_factory=NamedTupleCursor) as curs:
            sql_select = """SELECT id, status_code, MAX(created_at)
                           AS max_created_at FROM public.url_checks
                           GROUP BY id, status_code"""
            curs.execute(sql_select)
            result = curs.fetchall()
            return result


def is_url_in_database(connection, url):
    with connection as con:
        with con.cursor(cursor_factory=NamedTupleCursor) as curs:
            sql_url = """SELECT CAST
                         (CASE WHEN EXISTS
                         (SELECT 1 FROM public.urls WHERE name = %s)
                         THEN 1 ELSE 0 END AS BIT);"""
            curs.execute(sql_url, (url,))
            result = int(curs.fetchone().bit)
            return result


def insert_check_result_with_id_url(connection, _id, status_code, h1,
                                    title, description):
    with connection as con:
        with con.cursor() as curs:
            sql_all_data = """INSERT INTO public.url_checks
                              (id, url_id, status_code, h1, title,
                              description)
                              VALUES (%s, default, %s, %s, %s, %s);"""
            curs.execute(sql_all_data,
                         (_id, status_code, h1, title, description,))
