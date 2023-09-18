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


# #-Navigate to login page---
@app.route("/login", methods=['GET', 'POST'])
def Login():
    return render_template('login.html')

#--- Navigate to register page ------
@app.route("/chooseUser", methods=['GET', 'POST'])
def chooseUser():
    return render_template('usertype.html')

#--- Navigation (if choose student / supervisor) ------
@app.route("/chooseUser2", methods=['GET', 'POST'])
def chooseUser2():
    return render_template('usertype-2.html')

#---Navigation (if choose student) --------
@app.route("/chooseStud", methods=['GET', 'POST'])
def chooseStud():
    return render_template('register-1.html')

#---Navigation (if choose student) --------
@app.route("/chooseStud2", methods=['GET', 'POST'])
def chooseStud2():
    return render_template('register-2.html')

#---Navigation (if choose supervisor)-------------
@app.route("/chooseSV", methods=['GET', 'POST'])
def chooseSV():
    return render_template('supervisor-register.html')

#---Navigation (if choose admin)-------------
@app.route("/chooseAdmin", methods=['GET', 'POST'])
def chooseAdmin():
    return render_template('admin-register.html')

#---Navigation (if choose company)-------------
@app.route("/chooseCompany", methods=['GET', 'POST'])
def chooseCompany():
    return render_template('company-register.html')

# login ---------------------------
@app.route("/userLogin1", methods=['GET', 'POST'])
def userLogin():
    # Output a message if something goes wrong...
    msg = 'Incorrect ID or password!'
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = db_conn.cursor()
        cursor.execute('SELECT * FROM Student WHERE stud_id = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['stud_id'] = account['stud_id']
            session['password'] = account['password']
            # Redirect to home page
            return 'Logged in successfully!'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect ID or password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


#---Register---------------------------------------------------------
@app.route("/addstud", methods=['POST'])
def AddStud():
    stud_id = request.form['stud_id'] 
    stud_name = request.form['stud_name']
    ic = request.form['ic']
    email = request.form['email']
    gender = request.form['gender']
    programme = request.form['programme']
    group = request.form['group']
    cgpa = request.form['cgpa']
    password = request.form['password']
    intern_batch = request.form['intern_batch']
    ownTransport = request.form['ownTransport']
    currentAddress = request.form['currentAddress']
    contactNo = request.form['contactNo']
    personalEmail = request.form['personalEmail']
    homeAddress = request.form['homeAddress']
    homePhone = request.form['homePhone']
    profile_img = request.files['profile_img']
    resume = request.files['resume']

    insert_sql = "INSERT INTO Student VALUES (%s, %s, %s, %s, %s, %s, %d, %lf, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if profile_img.filename == "":
        return "Please select a file"
    if resume.filename == "":
        return "Please select a file"

    try:
        cursor = db_conn.cursor()
        cursor.execute(insert_sql, (stud_id, stud_name, ic, email, gender, programme, group, cgpa, password, intern_batch, ownTransport, currentAddress, contactNo
                                    , personalEmail, homeAddress, homeAddress, homePhone))
        db_conn.commit()
        cursor.close()
    except Exception as e:
        db_conn.rollback()  # Rollback the transaction in case of an error
        print(f"Error: {str(e)}")  # Print the error for debugging

        # Uplaod image file in S3 #
        profile_img_in_s3 = "stud-id-" + str(stud_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=profile_img_in_s3, Body=profile_img)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                stud_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddStudOutput.html', name=stud_name)

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
@app.route("/editCompany", methods=['GET', 'POST'])
def editCompany():
    id = "1"
    
    #Company Profile
    statement = "SELECT * FROM Company WHERE com_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (id))
    result = cursor.fetchone()
    cursor.close()
    
    return render_template('editCompany.html', com=result)

@app.route("/updateCompany", methods=['POST'])
def updateCompany():
    
    com_id = 1
    com_name =  request.form['com_name']
    total_staff =  request.form['total_staff']
    industry_invlove =  request.form['industry_invlove']
    com_name =  request.form['product_service']
    product_service =  request.form['product_service']
    company_website =  request.form['company_website']
    nearest_station =  request.form['nearest_station']
    com_address =  request.form['com_address']
    ssm = request.files['ssm_new']
    person_incharge =  request.form['person_incharge']
    email =  request.form['email']
    password =  request.form['password']

    if resume.filename == "":
        statement = "UPDATE Company SET com_name = %s, total_staff = %s, industry_involve = %s, product_service = %s, company_website = %s, OT_claim = %s, nearest_station = %s, com_address = %s, logo = %s, person_incharge = %s, contact_no = %s , password = %s WHERE com_id = %s;"
        cursor = db_conn.cursor()
        cursor.execute(statement, (job_title, job_desc, job_salary, job_location, workingDay, workingHour, accommodation, intern_id))
        db_conn.commit()  # Commit the changes to the database
       
    else:
          try:
            ssm_in_key = "con_id-" + str(com_id) + "_pdf"
            s3 = boto3.resource('s3')
              
            print("Data inserted in MySQL RDS... uploading pdf to S3...")
            s3.Bucket(custombucket).put_object(Key=ssm_in_s3, Body=ssm, ContentType=ssm.content_type)
    
            # Generate the object URL
            object_url = f"https://{custombucket}.s3.amazonaws.com/{ssm_in_s3}"
            statement = "UPDATE Company SET com_name = %s, total_staff = %s, industry_involve = %s, product_service = %s, company_website = %s, OT_claim = %s, nearest_station = %s, com_address = %s, logo = %s, person_incharge = %s, contact_no = %s , password = %s WHERE com_id = %s;"
            cursor.execute(statement, (ic, gender, programme, group, cgpa, password, intern_batch, ownTransport, currentAddress, contactNo, personalEmail, homeAddress, homePhone, object_url, stud_id))
            db_conn.commit()  # Commit the changes to the database
          except Exception as e:
            return str(e)
 
    return redirect("/goProfile/")



#==ADMIN========================================================================
@app.route("/StudentApp", methods=['GET', 'POST'])
def ApprovingStudent():
    return redirect('/studentapproval')

@app.route("/CompanyApp", methods=['GET', 'POST'])
def ApprovingCompany():
    return redirect('/companyapproval')

@app.route("/Supervisor", methods=['GET', 'POST'])
def ManagingSupervisor():
    return redirect('/viewsupervisor')

@app.route("/Dashboard", methods=['GET', 'POST'])
def AddingAdmin():
    return render_template('Dashboard.html')

#--Manage Admin---
@app.route('/addadmin', methods=['POST', 'GET'])
@csrf.exempt 
def add_admin():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO Admin (id, name, email, password) VALUES (%s, %s, %s, %s)", (id, name, email, password))
        db_conn.commit()

        # Redirect to a success page or do something else as needed
        return redirect('/viewadmin')

    return render_template('AdminIndex.html')  

@app.route('/viewadmin', methods=['GET'])
def view_admin():
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Admin")
        admins = cursor.fetchall()
        cursor.close()

        return render_template('AdminIndex.html', admins=admins)

    except Exception as e:
        return str(e)

@app.route('/deleteadmin', methods=['POST', 'GET'])
def delete_admin():
     if request.method == 'POST':
        id=request.form['id']

        delete_sql="DELETE FROM Admin WHERE id = %s"
        cursor = db_conn.cursor()
        cursor.execute(delete_sql, (id))
        db_conn.commit()
        cursor.close()

        return redirect('/viewadmin')
     return "Method Not Allowed", 405  # Handle GET requests with an error response

#--Student Approval---
@app.route("/studentapproval", methods=['GET'])
def StudAproval():
    try:
        statement = "SELECT id, stud_id, status FROM StudApproval WHERE status = %s"
        cursor = db_conn.cursor()
        cursor.execute(statement, ("pending"))

        # Fetch all the results
        results = cursor.fetchall()

        stud_approvals = []  # List to store StudApproval data

        for result in results:
            id, stud_id, status = result
            stud_approvals.append({
                'id': id,
                'stud_id': stud_id,
                'status': status,
            })

        return render_template('StudentApproval.html', stud_approvals=stud_approvals)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

@app.route("/updatestudentstatus", methods=['POST', 'GET'])
@csrf.exempt  
def UpdateStudStatus():
    try:
        id = request.form['id']
        new_status = request.form['status']

        # SQL statement to update the status of a StudApproval entry by id
        update_sql = "UPDATE StudApproval SET status = %s WHERE id = %s"
        cursor = db_conn.cursor()
        cursor.execute(update_sql, (new_status, id))
        db_conn.commit()
        cursor.close()
        
        return redirect("/studentapproval")

    except Exception as e:
        return str(e)

#--company approval---
@app.route("/companyapproval", methods=['GET'])
def ComApproval():
    try:
        statement = "SELECT id, com_id, status FROM ComApproval WHERE status = %s"
        cursor = db_conn.cursor()
        cursor.execute(statement, ("pending"))

        # Fetch all the results
        results = cursor.fetchall()

        com_approvals = []  # List to store StudApproval data

        for result in results:
            id, com_id, status = result
            com_approvals.append({
                'id': id,
                'com_id': com_id,
                'status': status,
            })

        return render_template('CompanyApproval.html', com_approvals=com_approvals)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

@app.route("/updatecompanystatus", methods=['POST', 'GET'])
@csrf.exempt  
def UpdateComStatus():
    try:
        id = request.form['id']
        new_status = request.form['status']

        # SQL statement to update the status of a StudApproval entry by id
        update_sql = "UPDATE ComApproval SET status = %s WHERE id = %s"
        cursor = db_conn.cursor()
        cursor.execute(update_sql, (new_status, id))
        db_conn.commit()
        cursor.close()
        
        return redirect("/companyapproval")

    except Exception as e:
        return str(e)

#--view and add supervisor---
@app.route("/createsupervisor", methods=['GET', 'POST'])
def AddingSupervisor():
    return render_template('AddSupervisor.html') 
    
@app.route("/addsupervisor", methods=['POST'])
@csrf.exempt  
def AddSupervisor():
    sv_id = request.form['sv_id']
    sv_name = request.form['sv_name']
    sv_email = request.form['sv_email']
    programme = request.form['programme']
    faculty = request.form['faculty']
    age = request.form['age']
    password = request.form['password']
    profile_image = request.files['profile_image']

    insert_sql = "INSERT INTO Supervisor VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if profile_image.filename == "":
        return "Please add a profile picture"
    
    if not allowed_file(profile_image.filename):
        return "File type not allowed. Only images (png, jpg, jpeg, gif) and PDFs are allowed."
    
    try:
        cursor.execute(insert_sql, (sv_id, sv_name, sv_email, programme, faculty, age, profile_image, password))
        db_conn.commit()
        
        profile_image_in_s3 = "sv_id-" + str(sv_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=profile_image_in_s3, Body=profile_image, ContentType=profile_image.content_type)
            
            # Generate the object URL
            object_url = f"https://{custombucket}.s3.amazonaws.com/{profile_image_in_s3}"

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    return redirect('/Supervisor')
   # return render_template('AddSupOutput.html', name=sv_name, email=sv_email, programme=programme, faculty=faculty, age=age, object_url=object_url)


@app.route("/searchsupervisor", methods=['POST'])
def GetSupervisor():
    try:
        supe = request.form['search']
        # Corrected SQL statement with placeholder
        statement = "SELECT sv_id, sv_name FROM Supervisor WHERE sv_name = %s"
        cursor = db_conn.cursor()
        cursor.execute(statement, (supe,))

        # Fetch the result
        result = cursor.fetchone()

        if result:
            sv_id, sv_name = result
            return render_template('searchSupervisor.html', name=sv_name, id=sv_id)
        else:
            return render_template('searchSupervisorError.html', id=supe)
        
    except Exception as e:
        return str(e)

    finally:
        cursor.close()
        
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

@app.route("/deletesupervisor", methods=['POST', 'GET'])
def DeleteSupervisor():
    if request.method == 'POST':
        sv_id = request.form['sv_id']

        # SQL statement to delete a supervisor by sv_id
        delete_sql = "DELETE FROM Supervisor WHERE sv_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(delete_sql, (sv_id,))
        db_conn.commit()
        cursor.close()
        
        return redirect("/viewsupervisor")

    return "Method Not Allowed", 405  # Handle GET requests with an error response

@app.route("/internship_index", methods=['GET'])
def display_internship():

    #Get All Internship
    home_statement = """SELECT i.intern_id, c.com_name, i.job_title, i.intern_salary, i.location, i.workingDay, i.workingHour, c.industry_involve 
    FROM Internship i INNER JOIN Company c WHERE i.com_id = c.com_id"""
    cursor = db_conn.cursor()
    cursor.execute(home_statement)
    result = cursor.fetchall()
    cursor.close()

    #Get Industry involve
    indus_statement = "SELECT cate_name FROM Category"
    cursor = db_conn.cursor()
    cursor.execute(indus_statement)
    indus = cursor.fetchall()
    cursor.close()

    return render_template('internship_index.html', internship = result, category = indus)    

@app.route('/internship_index/job_details/<int:id>')
def jobDetails(id):

    #Get Internship details
    details_statement = """SELECT i.intern_id, c.com_name, i.job_title, i.intern_salary, i.location, i.workingDay, i.workingHour, i.accommodation, i.job_description, c.product_service, c.industry_involve, c.person_incharge, c.contact_no, c.email 
    FROM Internship i INNER JOIN Company c WHERE i.com_id = c.com_id AND intern_id = %s"""
    cursor = db_conn.cursor()
    cursor.execute(details_statement, (id))
    details = cursor.fetchone()
    cursor.close()
    
    return render_template('job_details.html', internship = details)

@app.route('/internship_index/job_listing/<string:cate>')
def jobList(cate):

    #Get Specific Listing 
    cate_statement = """SELECT i.intern_id, c.com_name, i.job_title, i.intern_salary, i.location, i.workingDay, i.workingHour, c.industry_involve 
                        FROM Internship i INNER JOIN Company c WHERE i.com_id = c.com_id AND c.industry_involve = %s """
    cursor = db_conn.cursor()
    cursor.execute(cate_statement, (cate))
    list = cursor.fetchall()
    cursor.close()
    
    return render_template('job_listing.html', listing = list, type = cate)



        
if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.run(host='0.0.0.0', port=80, debug=True)
