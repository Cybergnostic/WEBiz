import csv
import hashlib

USERS_CSV = 'users.csv'

def hash_password(password):
    # Hash the password using SHA-256
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def authenticate_user(username, password):
    with open(USERS_CSV, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username and row['password'] == hash_password(password):
                return True
    return False

def get_user_alias(username):
    with open(USERS_CSV, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username:
                return row['alias']
    return None
