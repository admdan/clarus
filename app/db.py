import mysql.connector
from flask import current_app

def get_db_connection():
    return mysql.connector.connect(
        host=current_app.config.get('MYSQL_HOST'),
        user=current_app.config.get('MYSQL_USER'),
        password=current_app.config.get('MYSQL_PASSWORD'),
        database=current_app.config.get('MYSQL_DB', 'itflask')
    )

