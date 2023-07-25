import sqlite3
import os
import user_login

def get_database_choices():
    db_files = [file for file in os.listdir() if file.endswith(".db")]
    return db_files

def initialize_or_open_db(db_name, columns=None):
    connection = sqlite3.connect(db_name)

    if columns:
        # Initialize a new database with the provided columns
        cursor = connection.cursor()
        column_names = ', '.join(columns)
        cursor.execute(f"CREATE TABLE IF NOT EXISTS data ({column_names})")
        connection.commit()
        print(f"Database '{db_name}' initialized with columns: {column_names}")
    else:
        # Fetch all table names in the database
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        if table_names:
            # If there are tables, prompt the user to choose one
            print(f"Database '{db_name}' contains the following tables:")
            for i, table_name in enumerate(table_names, 1):
                print(f"{i}. {table_name}")

            while True:
                try:
                    table_choice = int(input("Enter the number corresponding to the table you want to use: "))
                    if 1 <= table_choice <= len(table_names):
                        break
                    else:
                        print("Invalid choice. Please enter a valid number.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")

            # Use the selected table
            table_name = table_names[table_choice - 1]

            # Print the columns of the selected table
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = cursor.fetchall()
            column_names = [col[1] for col in existing_columns]
            print(f"Database '{db_name}', Table '{table_name}'")
            print("Columns: " + ", ".join([f"{i + 1}. {col}" for i, col in enumerate(column_names)]))

            return connection, table_name
        else:
            print(f"Database '{db_name}' does not contain any tables.")

    return connection, None

def delete_row(connection, table_name):
    cursor = connection.cursor()

    # Get the primary key column name (assuming it's 'id')
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    primary_key_column = next((col[1] for col in columns if col[5]), None)

    if not primary_key_column:
        print("No primary key column found. Unable to delete rows.")
        return

    # Get the current rows in the table
    cursor.execute(f"SELECT {primary_key_column}, * FROM {table_name}")
    rows = cursor.fetchall()

    # Display the rows to the user
    print("Available Rows:")
    for i, row in enumerate(rows, 1):
        print(f"{i}. {row}")

    while True:
        try:
            row_choice = int(input("Enter the number corresponding to the row you want to delete: "))
            if 1 <= row_choice <= len(rows):
                break
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    # Get the primary key value of the row to delete
    row_to_delete = rows[row_choice - 1][0]

    # Construct the query to delete the row
    query = f"DELETE FROM {table_name} WHERE {primary_key_column} = ?"
    cursor.execute(query, (row_to_delete,))
    connection.commit()
    print(f"Row with {primary_key_column} = {row_to_delete} has been deleted.")

def delete_all_entries(connection, table_name):
    cursor = connection.cursor()

    # Construct the query to delete all entries
    query = f"DELETE FROM {table_name}"
    cursor.execute(query)
    connection.commit()
    print("All entries have been deleted.")

def insert_new_column(connection, table_name):
    cursor = connection.cursor()

    # Get the user input for the new column position
    while True:
        try:
            position = int(input("Insert new column at which position (0 to n+1): "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    # Get the existing column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = cursor.fetchall()
    column_names = [col[1] for col in existing_columns]

    # Get the new column name from the user
    new_column_name = input("Enter the new column name: ")

    # Calculate the index to insert the new column
    index = max(0, min(position - 1, len(column_names)))

    # Construct the ALTER TABLE query to add the new column
    if index == len(column_names):
        # Inserting at the end
        query = f"ALTER TABLE {table_name} ADD COLUMN {new_column_name}"
    else:
        # Inserting between two columns
        column_before = column_names[index]
        query = f"ALTER TABLE {table_name} ADD COLUMN {new_column_name} AFTER {column_before}"

    cursor.execute(query)
    connection.commit()
    print(f"Column '{new_column_name}' added at position {index + 1}")

def delete_column(connection, table_name):
    cursor = connection.cursor()

    # Get the existing column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = cursor.fetchall()
    column_names = [col[1] for col in existing_columns]

    # Get the column to be deleted from the user
    print("Current Columns:")
    for i, col in enumerate(column_names, 1):
        print(f"{i}. {col}")

    while True:
        try:
            col_choice = int(input("Enter the number corresponding to the column you want to delete: "))
            if 1 <= col_choice <= len(column_names):
                break
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    column_to_delete = column_names[col_choice - 1]

    # Construct the query to delete the column
    query = f"ALTER TABLE {table_name} DROP COLUMN {column_to_delete}"

    cursor.execute(query)
    connection.commit()
    print(f"Column '{column_to_delete}' and its entries have been deleted.")



if __name__ == "__main__":
    # Get a list of database choices
    database_choices = get_database_choices()

    if not database_choices:
        print("No databases (.db files) found in the root folder.")
        exit()

    print("Available Databases:")
    for i, db_choice in enumerate(database_choices, 1):
        print(f"{i}. {db_choice}")

    while True:
        try:
            db_choice = int(input("Enter the number corresponding to the database you want to work with: "))
            if 1 <= db_choice <= len(database_choices):
                break
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    db_name = database_choices[db_choice - 1]
    connection, table_name = initialize_or_open_db(db_name)
    
    if table_name:
        # Prompt the user to choose an action
        while True:
            print("\nChoose an action:")
            print("1. Insert new column")
            print("2. Delete a column and its entries")
            print("3. Delete a row")
            print("4. Delete all entries")
            if db_name == 'users.db':
                print("5. Add a new user")
            print("6. Exit")

            try:
                choice = int(input("Enter the number corresponding to your choice: "))
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                continue

            if choice == 1:
                insert_new_column(connection, table_name)
            elif choice == 2:
                delete_column(connection, table_name)
            elif choice == 3:
                delete_row(connection, table_name)
            elif choice == 4:
                delete_all_entries(connection, table_name)
            elif choice == 5 and db_name == 'users.db':
                # Ask for additional information to create a new user
                username, password = input("Enter the username and password (separated by a space): ").split()
                title = input("Enter the title: ")
                speciality = input("Enter the speciality: ")
                name = input("Enter the name: ")
                surname = input("Enter the surname: ")
                alias = input("Enter the alias: ")
                user_login.add_user(username, password, title, speciality, name, surname, alias)
            elif choice == 6:
                break
            else:
                print("Invalid choice. Please enter a valid number.")

    connection.close()
    