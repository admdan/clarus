import psycopg2
import psycopg2.extras
from flask import current_app

def get_db_connection():
    schema = current_app.config.get('POSTGRES_SCHEMA', 'public')
    conn = psycopg2.connect(
        host=current_app.config.get('POSTGRES_HOST'),
        port=current_app.config.get('POSTGRES_PORT'),
        user=current_app.config.get('POSTGRES_USER'),
        password=current_app.config.get('POSTGRES_PASSWORD'),
        dbname=current_app.config.get('POSTGRES_DB'),
        options = f'-c search_path={schema}'
    )
    return conn


