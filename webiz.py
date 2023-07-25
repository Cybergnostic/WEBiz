import csv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
# import os
import pandas as pd
import user_login

app = Flask(__name__)

# Set a secret key for the session to enhance security
app.secret_key = 'your_secret_key_here'

# Configuration for the SQLite database
DATABASE = 'patients.csv'
CSV_FILE = 'dg.csv'
DATA = 'users.csv'

def load_user_data(data_file):
    # Load user data from the CSV file into a DataFrame
    try:
        df = pd.read_csv(data_file, encoding='utf-8')
        return df
    except FileNotFoundError:
        print(f"Error: The '{data_file}' file not found.")
        return None

def get_user_alias(username):
    # This function has been updated to fetch 'alias' instead of 'user_alias'
    with connect_db(DATA) as conn:
        cursor = conn.cursor()
        query = "SELECT alias FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        return result[0] if result else None

def save_data_to_csv(data):
    # Save the data to the CSV file along with the user's alias
    with open('patients.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['patient_surname', 'patient_name', 'patient_fathername', 'patient_birthdate', 'anamnesis', 'diagnosis_search', 'therapy', 'alias']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Check if the file is empty. If yes, write the header row.
        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow(data)


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
        session['logged_in'] = "empty"
        # Authenticate user using the authenticate_user function from user_login module
        if user_login.authenticate_user(username, password):
            print("User authenticated successfully.")
            # The user is authenticated, set the 'logged_in' session variable to True
            session['logged_in'] = user_login.get_user_alias(username)
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

    # Load user data from the CSV file into a DataFrame
    df = load_user_data(DATA)

    if df is None:
        # Handle the case when data cannot be loaded from the CSV file
        return "An error occurred while loading user data."

    # Fetch the user's data from the DataFrame based on the current logged-in user's alias
    user_data = None
    alias = session.get('logged_in')
    print("Logged-in alias:", alias)

    # Check if the DataFrame is empty or not before accessing its elements
    if not df.empty:
        if alias is not None:
            # Use .loc to filter the DataFrame based on the alias
            filtered_df = df.loc[df['alias'] == alias]
            if not filtered_df.empty:
                user_data = filtered_df.iloc[0].to_dict()
            else:
                print("User data not found.")
        else:
            print("Alias is None. User not authenticated.")
    else:
        print("DataFrame is empty. User data not found.")

    # Fetch the doctor's information
    doctor_data = {
        'title': user_data.get('title', ''),
        'name': user_data.get('name', ''),
        'surname': user_data.get('surname', ''),
        'speciality': user_data.get('speciality', '')
    }

    # Render the main index page here and pass the user_data and doctor_data to the template
    return render_template('main_index.html', data=user_data, doctor=doctor_data)

    
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

        # Get the user's alias from the session
        alias = session.get('logged_in')

        # Save the data to the CSV file along with the user's alias
        data = {
            'patient_surname': patient_surname,
            'patient_name': patient_name,
            'patient_fathername': patient_fathername,
            'patient_birthdate': patient_birthdate,
            'anamnesis': anamnesis,
            'diagnosis_search': diagnosis_search,
            'therapy': therapy,
            'alias': alias,
        }

        save_data_to_csv(data)

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

    # Run the Flask app
    app.run(host='192.168.100.60', port=777)
