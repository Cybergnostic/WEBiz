import csv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
# import os
import pandas as pd
import user_login

app = Flask(__name__)

# Set a secret key for the session to enhance security
app.secret_key = 'your_secret_key_here'

# Configuration for the SQLite database
DATABASE = 'patients.db'
CSV_FILE = 'dg.csv'




@app.route('/')
def login_page():
    # If the user is already logged in, redirect them to the index page
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('index'))

    # Otherwise, show the login page
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Login form submitted with username: {username} and password: {password}")

        # Authenticate user using the authenticate_user function from user_login module
        if user_login.authenticate_user(username, password):
            print("User authenticated successfully.")
            # The user is authenticated, set the 'logged_in' session variable to True
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            print("User authentication failed.")
            # The user login failed, redirect them back to the login page with an error message.
            return redirect(url_for('login_page'))

# Add a logout route to clear the session when the user logs out
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Clear the session to log the user out
    session.clear()
    return redirect(url_for('login_page'))


@app.route('/index')
def index():
    # Check if the user is logged in. If not, redirect to the login page.
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login_page'))

    # Fetch the user's data from the database based on the current logged-in user's username
    user_data = None
    if 'username' in session:
        with user_login.connect_db() as conn:
            try:
                cursor = conn.cursor()
                # Print the SQL query before executing it
                query = "SELECT title, surname, name, speciality FROM users WHERE username = ?"
                print("SQL Query:", query)
                
                cursor.execute(query, (session['username'],))
                user_data = cursor.fetchone()
            except Exception as e:
                print(f"Error occurred while fetching user data: {e}")

    # Print the content of the 'user_data' variable
    print("User Data:", user_data)

    # Render the main index page here and pass the user_data to the template as 'user_data'
    return render_template('main_index.html', data=user_data)
    
    
@app.route('/save', methods=['POST'])
def save_data():
    if request.method == 'POST':
        patient_surname = request.form['patient_surname']
        patient_name = request.form['patient_name']
        patient_fathername = request.form['patient_fathername']
        patient_birthdate = request.form['patient_birthdate']
        anamnesis = request.form['anamnesis']
        diagnosis_search = request.form['diagnosis_search']
        therapy = request.form['therapy']
        print(patient_surname, patient_name, patient_fathername, patient_birthdate, anamnesis, diagnosis_search, therapy)
        # Save the data to the database
        with user_login.connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO patients (patient_surname, patient_name, patient_fathername, patient_birthdate, anamnesis, diagnosis_search, therapy) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (patient_surname, patient_name, patient_fathername, patient_birthdate, anamnesis, diagnosis_search, therapy) )
            conn.commit()

        # Return a JSON response indicating success
        return jsonify({"message": "Data saved successfully."})

    # If the request method is not POST, return an error response
    return jsonify({"error": "Invalid request method."}), 400


@app.route('/get_suggestions')
def get_suggestions():
    keyword = request.args.get('keyword', '').lower()
    suggestions = []

    # Read the CSV file and find the top 10 matches based on 'Oznaka', 'Naziv dijagnoze', and 'Latinski naziv dijagnoze'
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            oznaka = row['Oznaka'].lower()
            naziv_dijagnoze = row['Naziv dijagnoze'].lower()
            latinski_naziv = row['Latinski naziv dijagnoze'].lower()
            if keyword in oznaka or keyword in naziv_dijagnoze or keyword in latinski_naziv:
                suggestions.append({
                    'Oznaka': row['Oznaka'],
                    'Naziv dijagnoze': row['Naziv dijagnoze'],
                    'Latinski naziv dijagnoze': row['Latinski naziv dijagnoze']
                })

    # Take the top 10 matches and return them as a list of suggestions
    suggestions = suggestions[:10]
    return jsonify(suggestions)


if __name__ == '__main__':
    app.run(host='192.168.100.60', port=777)