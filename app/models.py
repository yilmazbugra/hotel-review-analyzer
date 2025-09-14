from app.db import get_db_connection
from datetime import datetime
from .db import db

class User:
    @staticmethod
    def get_all():
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        connection.close()
        return users

    @staticmethod
    def get_by_id(user_id):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        connection.close()
        return user

    @staticmethod
    def delete(user_id):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        connection.close()

    @staticmethod
    def update(user_id, name, email):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET first_name = %s, email = %s WHERE id = %s", (name, email, user_id))
        connection.commit()
        connection.close()

    @staticmethod
    def create(name, email, password, role='user'):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (first_name, email, password, role) VALUES (%s, %s, %s, %s)",
                       (name, email, password, role))
        connection.commit()
        connection.close()
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy




class Favorite(db.Model):
    __tablename__ = 'favorite'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    url = db.Column(db.String(500))
    analysis = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    order_index = db.Column(db.Integer, default=0)


from flask_login import UserMixin
from app.db import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('admin', 'staff', 'user'), default='user')
    created_at = db.Column(db.DateTime)

    def get_id(self):
        return str(self.id)

class ReviewResult(db.Model):
    __tablename__ = "review_result"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_reviews = db.Column(db.Integer)
    positive_count = db.Column(db.Integer)
    negative_count = db.Column(db.Integer)
    positive_keywords = db.Column(db.Text)
    negative_keywords = db.Column(db.Text)
    score = db.Column(db.Float)
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CalendarEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=True)  
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=True)
