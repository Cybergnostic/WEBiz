import csv
import hashlib

DATA = 'users.csv'  # Update the file path accordingly

def get_hashed_password(password):
    # Hash the password using SHA256
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash

def add_user(username, password, title, speciality, name, surname, alias):
    # Get the hashed password
    hashed_password = get_hashed_password(password)

    # Save the user information to the CSV file with UTF-8 encoding
    with open(DATA, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([username, hashed_password, title, speciality, name, surname, alias])
    print(f"User '{username}' has been added to the database.")



def main():
    print("Welcome to the User Creation Tool!")
    username = input("Enter username: ")
    password = input("Enter password: ")
    title = input("Enter title: ")
    speciality = input("Enter speciality: ")
    name = input("Enter name: ")
    surname = input("Enter surname: ")
    alias = input("Enter alias: ")

    add_user(username, password, title, speciality, name, surname, alias)

if __name__ == '__main__':
    main()
