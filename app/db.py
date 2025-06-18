import mysql.connector
from flask import current_app

def get_db_connection():
    return mysql.connector.connect(
        host=current_app.config.get('MYSQL_HOST', 'localhost'),
        user=current_app.config.get('MYSQL_USER', 'root'),
        password=current_app.config.get('MYSQL_PASSWORD', 'Xchaosweaver24!'),
        database=current_app.config.get('MYSQL_DB', 'itflask')
    )

