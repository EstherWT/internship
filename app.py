from flask_wtf.csrf import CSRFProtect, CSRFError
from flask import Flask, render_template, request, redirect, flash, jsonify
from pymysql import connections
import os
import boto3

customhost = "internshipdatabase.cpkr5ofaey5p.us-east-1.rds.amazonaws.com"
customuser = "admin"
custompass = "admin123"
customdb = "internshipDatabase"
custombucket = "hwt-internship"
customregion = "us-east-1"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

app = Flask(__name__, static_folder='assets')
#encrypt
csrf = CSRFProtect(app)
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

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

#---Navigate to page only----------------------------------------------

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/internshipPublication", methods=['GET', 'POST'])
def publichInternPage():
    return render_template('publishIntern.html')

#go profile with login check -------------------------------------------

@app.route("/goProfile", methods=['GET', 'POST'])
def goProfile():

    id = "1"
    
    #Company Profile
    statement = "SELECT * FROM Company WHERE com_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (id))
    result = cursor.fetchone()
    cursor.close()
    
    return render_template('viewCompany.html', com=result)

#---With function--------------------------------------------------------------------
#==INTERNSHIP========================================================================
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
    
    #Get last ID
    countstatement = "SELECT intern_id FROM Internship ORDER BY intern_id DESC LIMIT 1;"
    count_cursor = db_conn.cursor()
    count_cursor.execute(countstatement)
    result = count_cursor.fetchone()
    intern_id = int(result[0]) + 1
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


@app.route("/goManageInternship", methods=['GET'])
def GoManageInternship():

    com_id = 1
    statement = "SELECT intern_id, job_title, intern_salary FROM Internship WHERE com_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (com_id))

    result = cursor.fetchall()
    cursor.close()
    
    return render_template('manageIntern.html', data=result)

@app.route('/viewIntern/<int:internship_id>')
def view_internship(internship_id):

    statement = "SELECT * FROM Internship WHERE intern_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (internship_id))
    result = cursor.fetchone()
    cursor.close()

    com_statement = "SELECT * FROM Company WHERE com_id = %s"
    com_cursor = db_conn.cursor()
    com_cursor.execute(com_statement, (result[1]))
    com_result = com_cursor.fetchone()
    com_cursor.close()

    return render_template('viewIntern.html', intern=result, com=com_result)

@app.route('/editIntern/<int:internship_id>')
def edit_internship(internship_id):

    statement = "SELECT * FROM Internship WHERE intern_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (internship_id))
    result = cursor.fetchone()

    return render_template('editIntern.html', intern=result)

@app.route('/updateIntern', methods=['POST'])
def update_internship():

    com_id = 1
    intern_id =  request.form['intern_id']
    job_title = request.form['job_title']
    job_desc = request.form['job_description']
    job_salary = request.form['job_salary']
    job_location = request.form['job_location']
    workingDay = request.form['workingDay']
    workingHour = request.form['workingHour']
    accommodation = request.form['accommodation']

    statement = "UPDATE Internship SET job_title = %s, job_description = %s, intern_salary = %s, location = %s, workingDay = %s, workingHour = %s, accommodation = %s WHERE intern_id = %s;"
    cursor = db_conn.cursor()
    cursor.execute(statement, (job_title, job_desc, job_salary, job_location, workingDay, workingHour, accommodation, intern_id))
    db_conn.commit()  # Commit the changes to the database

    return redirect("/viewIntern/" + intern_id)

@app.route('/deleteIntern/<int:internship_id>')
def delete_internship(internship_id):

    statement = "DELETE FROM Internship WHERE intern_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (internship_id))
    cursor.close()
    db_conn.commit()

    return redirect("/goManageInternship")

#==COMPANY========================================================================



#==ADMIN========================================================================
@app.route("/StudentApp", methods=['GET', 'POST'])
def ApprovingStudent():
    return redirect('/studentapproval')

@app.route("/CompanyApp", methods=['GET', 'POST'])
def ApprovingCompany():
    return redirect('/companyapproval')
    
#--view supervisor---
@app.route("/viewsupervisor", methods=['GET'])
def ViewSupervisor():
    try:
        statement = "SELECT sv_id, sv_name, sv_email, programme, faculty, age, profile_image FROM Supervisor"
        cursor = db_conn.cursor()
        cursor.execute(statement)

        # Fetch all the results
        results = cursor.fetchall()

        supervisors = []  # List to store supervisor data

        for result in results:
            sv_id, sv_name, sv_email, programme, faculty, age, profile_image = result
            supervisors.append({
                'sv_id': sv_id,
                'sv_name': sv_name,
                'sv_email': sv_email,
                'programme': programme,
                'faculty': faculty,
                'age': age,
                'profile_image': profile_image,
            })

        return render_template('ViewSupervisor.html', supervisors=supervisors)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()




        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
