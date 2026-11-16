
import os
import re

from flask import Flask, request, render_template_string
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)


# 1. Connect to MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "contact_db")
    )


# 2. Create contacts table
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                message TEXT NOT NULL
            )
        """)
        conn.commit()
        print("Contacts table created successfully!")

    finally:
        cursor.close()
        conn.close()


# 3. HTML Contact Form
html = """
<!DOCTYPE html>
<html>
<head>
    <title>Contact Form</title>

    <style>
        body {
            font-family: Arial;
            background-color: #f2f2f2;
            padding: 30px;
        }

        .container {
            background: white;
            padding: 25px;
            width: 350px;
            margin: auto;
            border-radius: 10px;
        }

        input, textarea {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            box-sizing: border-box;
        }

        button {
            background-color: green;
            color: white;
            padding: 10px;
            border: none;
            width: 100%;
            cursor: pointer;
        }
    </style>
</head>

<body>

<div class="container">

    <h2>Contact Us</h2>

    <form method="POST" action="/">

        <label>Name:</label>
        <input type="text" name="name" required maxlength="255">

        <label>Email:</label>
        <input type="email" name="email" required maxlength="255">

        <label>Message:</label>
        <textarea name="message" required></textarea>

        <button type="submit">Submit</button>

    </form>

    <p>{{ result }}</p>

</div>

</body>
</html>
"""


# 4. Contact Form route
@app.route("/", methods=["GET", "POST"])
def contact_form():

    result = ""

    if request.method == "POST":

        # Get form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        # Validate empty fields
        if not name or not email or not message:
            result = "All fields are required."

        # Validate email
        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            result = "Invalid email address."

        else:
            conn = None
            cursor = None

            try:
                conn = get_db_connection()
                cursor = conn.cursor()

                # Insert data securely using parameterized query
                sql = """
                    INSERT INTO contacts (name, email, message)
                    VALUES (%s, %s, %s)
                """

                values = (name, email, message)

                cursor.execute(sql, values)
                conn.commit()

                result = "Message submitted successfully!"

            except mysql.connector.Error as error:
                result = "Database error. Please try again."
                print("Database error:", error)

            finally:
                if cursor is not None:
                    cursor.close()

                if conn is not None:
                    conn.close()

    return render_template_string(html, result=result)


# 5. Run application
if __name__ == "__main__":

    try:
        create_table()
        print("Database connected successfully!")

        app.run(host="127.0.0.1", port=5000, debug=False)

    except mysql.connector.Error as error:
        print("Unable to connect to database:", error)
