from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3

customhost = "internshipdatabase.cpkr5ofaey5p.us-east-1.rds.amazonaws.com"
customuser = "admin"
custompass = "admin123"
customdb = "internshipDatabase"
custombucket = "hwt-internship"
customregion = "us-east-1"


app = Flask(__name__, static_folder='assets')

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('publishIntern.html')

@app.route("/addInternFormCom", methods=['POST'])
def AddInternFormCom():

    com_id = 1
    job_title = request.form['job_title']
    job_desc = request.form['job_description']
    job_salary = request.form['job_salary']
    job_location = request.form['job_location']
    workingDay = request.form['workingDay']
    workingHour = request.form['workingHour']
    accommodation = request.form['accommodation']

    #Get total ID
    countstatement = "SELECT COUNT(*) FROM Internship"
    count_cursor = db_conn.cursor()
    count_cursor.execute(countstatement)
    result = cursor.fetchone()
    intern_id = result[0] + 1
    count_cursor.close()

    insert_sql = "INSERT INTO Internship VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

    try:
        # Attempt to execute the SQL INSERT statement
        cursor = db_conn.cursor()
        cursor.execute(insert_sql, (intern_id, com_id, job_title, job_desc, job_salary, job_location, workingDay, workingHour, accommodation))
        db_conn.commit()  # Commit the transaction
        cursor.close()
    except Exception as e:
        db_conn.rollback()  # Rollback the transaction in case of an error
        print(f"Error: {str(e)}")  # Print the error for debugging

    
    return render_template('publishInternSuccess.html', intern=job_title)


@app.route("/goManageInternship", methods=['POST'])
def GoManageInternship():

    com_id = 1
    statement = "SELECT job_title, intern_salary FROM Internship WHERE com_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (com_id))

    result = cursor.fetchone()
    cursor.close()

    return render_template('test.html', a=result)


        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
