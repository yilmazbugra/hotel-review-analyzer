import pymysql

def get_db_connection():
    """MySQL veritabanı bağlantısı."""
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='bugra123',
        database='hotel_system',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
