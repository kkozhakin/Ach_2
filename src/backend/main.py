import os
import sys

import mysql.connector
from mysql.connector import Error, OperationalError
from flask import Flask, request, redirect

template_dir = os.path.abspath('static')
app = Flask(__name__, template_folder=template_dir)

url_front = os.environ.get('URL_FRONT')
port_front = os.environ.get('PORT_FRONT')
port = os.environ.get('PORT_BACK')
url_db = os.environ.get('URL_DB')
port_db = os.environ.get('PORT_DB')


def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
        sys.stderr.write(f"The error '{e}' occurred")

    return connection


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
        sys.stderr.write(f"The error '{e}' occurred")
        return result


def execute_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        return 0
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        sys.stderr.write(f"The error '{e}' occurred")
        return 1


@app.route('/', methods=['POST'])
def main():
    error_code = 0
    data = request.form.get('number')
    print("DATA:")
    print(data)

    if data is None:
        return '<h1>No number</h1>'

    connection = create_connection("db", "root", "passwd", "lab_db")
    if connection is None:
        sys.stderr.write("Error connecting DB")
        error_code = 3

    check1 = execute_read_query(connection, 'SELECT COUNT(num) FROM numbers WHERE num=' + str(data) + ';')
    if check1[0][0] > 0:
        sys.stderr.write("This number exists (ERROR #1)")
        error_code = 1

    check2 = execute_read_query(connection, 'SELECT COUNT(num) FROM numbers WHERE num=' + str(int(data)+1) + ';')
    if check2[0][0] > 0:
        sys.stderr.write("This number lower (ERROR #2)")
        error_code = 2

    if execute_query(connection, 'INSERT INTO numbers (num) VALUES (' + str(data) + ');') != 0:
        sys.stderr.write("Error inserting into DB")
        error_code = 3

    return redirect("http://0.0.0.0/?err="+str(error_code)+"&number="+str(data))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
