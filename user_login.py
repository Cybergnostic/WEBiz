import sqlite3
from flask import session
import hashlib
import webiz as w

DATA = 'users.db'


def connect_db(db_file):
    try:
        return sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def authenticate_user(username, password):
    print(f"Authenticating user: {username}")
    # Hash the provided password using SHA256
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    print(f"Password hash: {password_hash}")

    with connect_db(DATA) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password_hash))
        user = cursor.fetchone()

        if user:
            # Set the 'logged_in' session variable to True for the authenticated user
            session['logged_in'] = True
            return True
        else:
            return False

def init_db():
    with connect_db(DATA) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

def add_user(username, password, title, speciality, name, surname):
    # Hash the password using SHA256
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Save the user information to the 'users' table
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (username, password, title, speciality, name, surname) VALUES (?, ?, ?, ?, ?, ?)",
                   (username, password_hash, title, speciality, name, surname))
    connection.commit()
    connection.close()
    print(f"User '{username}' has been added to the database.")
        


def init_db_scratch(*columns):
    with connect_db() as conn:
        cursor = conn.cursor()
        column_str = ', '.join(f'{col} TEXT NOT NULL' for col in columns)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {column_str}
            )
        ''')
        conn.commit()

# init_db()
# add_user("jovke", "car", "prof. dr", "ginekolog", "Jovan", "Veljkovic")