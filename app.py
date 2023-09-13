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
    cursor = db_conn.cursor()
    cursor.execute(countstatement)
    result = cursor.fetchone()
    intern_id = result[0] + 1

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
    finally:
        db_conn.close()  # Close the database connection
    
    return render_template('publishInternSuccess.html', intern=job_title)




@app.route("/searchstud", methods=['POST'])
def GetStud():
    try:
        stud = request.form['search']

        # Corrected SQL statement with placeholder
        statement = "SELECT stud_id, stud_name FROM student WHERE stud_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(statement, (stud,))
        
        # Fetch the result
        result = cursor.fetchone()

        if result:
            stud_id, stud_name = result
            return render_template('searchStudent.html', name=stud_name, id=stud_id)
        else:
            return render_template('searchError.html', id=stud)
        
    except Exception as e:
        return str(e)
        
    finally:
        cursor.close()


@app.route("/updatestud", methods=['POST'])
def UpStud():
    try:
        stud = request.form['update_id']
        name = request.form['update_name']

        # Corrected SQL statement with placeholder
        statement_get = "SELECT stud_name FROM student WHERE stud_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(statement_get, (stud,))
        
        # Fetch the result
        result = cursor.fetchone()

        if result:

            stud_name = result[0]
            statement = "UPDATE student SET stud_name = %s WHERE stud_id = %s"
            cursor.execute(statement, (name, stud))
          
            return render_template('updateStudent.html', new=name, id=stud, old=stud_name)
        else:
            return render_template('updateError.html', id=stud)
        
    except Exception as e:
        return str(e)
        
    finally:
        cursor.close()


        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
