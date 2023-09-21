from flask import Flask, render_template, request, redirect, url_for, session
from pymysql import connections
import os
import boto3
from config import *
import hashlib
import urllib.parse

app = Flask(__name__)
app.secret_key = 'my_super_secret_key_12345'

# Configure the 'templates' folder for HTML templates.
app.template_folder = 'pages'
app.static_folder = 'static'

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
table = 'students'


@app.route("/", methods=['GET'], endpoint='index')
def index():
    return render_template('index.html')


@app.route("/job_listing", methods=['GET'])
def job_listing():
    return render_template('job_listing.html')


@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')


@app.route("/blog", methods=['GET'])
def blog():
    return render_template('blog.html')


@app.route("/single_blog", methods=['GET'])
def single_blog():
    return render_template('single_blog.html')


@app.route("/elements", methods=['GET'])
def elements():
    return render_template('elements.html')


@app.route("/job_details", methods=['GET'])
def job_details():
    return render_template('job_details.html')


@app.route("/contact", methods=['GET'])
def contact():
    return render_template('contact.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']
        ic = request.form['ic']
        programmeSelect = request.form['programmeSelect']
        tutorialGrp = request.form['tutorialGrp']
        studentID = request.form['studentID']
        cgpa = request.form['cgpa']
        ucSupervisor = request.form['ucSupervisor']
        ucSupervisorEmail = request.form['ucSupervisorEmail']

        # Check if the email is already in the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM students WHERE stud_email=%s", (email))
        results = cursor.fetchall()
        cursor.close()

        # If the email is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('register.html', email_error="The email is already in use.")

        # Otherwise, check if the IC is already in the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM students WHERE ic=%s", (ic))
        results = cursor.fetchall()
        cursor.close()

        # If the IC is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('register.html', ic_error="The IC is already in use.")

        # Otherwise, check if the student ID is already in the database.
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT * FROM students WHERE studentID=%s", (studentID))
        results = cursor.fetchall()
        cursor.close()

        # If the student ID is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('register.html', studentID_error="The student ID is already in use.")

        insert_sql = "INSERT INTO students VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        try:
            cursor.execute(insert_sql, (studentID,
                                        firstName,
                                        lastName,
                                        gender,
                                        email,
                                        password,
                                        ic,
                                        programmeSelect,
                                        tutorialGrp,
                                        cgpa,
                                        ucSupervisor
                                        ))
            db_conn.commit()
            cursor.close()
            # Redirect to the homepage after successful registration
            return redirect(url_for('login'))
        except Exception as e:
            cursor.close()
            return str(e)  # Handle any database errors here

    return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if role == 'Student':
            # Fetch data from the database here
            cursor = db_conn.cursor()
            select_sql = "SELECT stud_email, password, firstName, studentID FROM students WHERE stud_email = %s"
            cursor.execute(select_sql, (email,))
            data = cursor.fetchone()  # Fetch a single row

            if data:
                # Data is found in the database
                stored_password = data[1]
                name = data[2]
                studID = data[3]

                # You should hash the provided password and compare it to the stored hashed password
                hashed_password = hashlib.sha256(password.encode()).hexdigest()

                if password == stored_password:
                    # Passwords match, user is authenticated
                    return render_template('index.html', user_login_name=name, studentID=studID, user_authenticated=True)
                else:
                    return render_template('login.html', pwd_error="Incorrect password. Please try again.")
            else:
                return render_template('login.html', email_login_error="Email not found. Please register or try a different email.")
        elif role == 'Company':
             # Fetch data from the database here
            cursor = db_conn.cursor()
            select_sql = "SELECT compEmail, comPassword, compName FROM company WHERE compEmail = %s"
            cursor.execute(select_sql, (email,))
            data = cursor.fetchone()  # Fetch a single row

            if data:
                # Data is found in the database
                stored_password = data[1]
                name = data[2]
                session['user_login_name'] = name

                if password == stored_password:
                    # Passwords match, user is authenticated
                    return redirect(url_for('companyDashboard'))
                else:
                    return render_template('login.html', pwd_error="Incorrect password. Please try again.")
            else:
                return render_template('login.html', email_login_error="Email not found. Please register or try a different email.")
            

    return render_template('login.html')


@app.route("/studentDashboard", methods=['GET'])
def studentDashboard():
    # Retrieve the studentID from the query parameters
    student_id = request.args.get('studentID')

    # Pass the studentID to the studentDashboard.html template
    return render_template('studentDashboard.html', studentID=student_id)


def list_files(bucket, path):
    contents = []
    folder_prefix = path

    for image in bucket.objects.filter(Prefix=folder_prefix):
        # Extract file name without the folder prefix
        file_name = image.key[len(folder_prefix):]
        if file_name:
            contents.append(file_name)

    return contents


@app.route("/form", methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        studID = request.form['studentID']

        uploaded_files = request.files.getlist('acceptanceForm') + \
            request.files.getlist('parentForm') + \
            request.files.getlist('letterForm') + \
            request.files.getlist('hireEvi')

        # Uplaod image file in S3 #
        # emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        # Create a folder or prefix for the files in S3
        # Replace 'your_folder_name' with your desired folder name
        folder_name = 'Student/' + studID + "/"

        list_files = []

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")

            for file in uploaded_files:
                list_files.append(file.filename)
                # Construct the key with the folder prefix and file name
                key = folder_name + file.filename

                # Upload the file into the specified folder
                s3.Bucket(custombucket).put_object(Key=key, Body=file)

                # Generate the object URL
                bucket_location = boto3.client(
                    's3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    file.filename)

        except Exception as e:
            return str('bucket', str(e))

        bucket = s3.Bucket(custombucket)

        # list_of_files = list_files(bucket)

        return render_template('form.html', my_bucket=bucket, studentID=studID, list_of_files=list_files)

    # Retrieve the studentID from the query parameters
    student_id = request.args.get('studentID')

    return render_template('form.html', studentID=student_id)


@app.route("/report", methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        studID = request.form['studentID']
        reportForm_files = request.files['reportForm']

        # Uplaod image file in S3
        s3 = boto3.resource('s3')

        # Create a folder or prefix for the files in S3
        folder_name = 'Student/' + studID + "/" + "report/"

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")

            filename = reportForm_files.filename.split('.')

            # Construct the key with the folder prefix and file name
            key = folder_name + filename[0] + "_progress_report." + filename[1]

            # Upload the file into the specified folder
            s3.Bucket(custombucket).put_object(Key=key, Body=reportForm_files)

            # Generate the object URL
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                key)

        except Exception as e:
            return str('bucket', str(e))

        bucket = s3.Bucket(custombucket)
        list_of_files = list_files(bucket, folder_name)

        return render_template('report.html', my_bucket=bucket, studentID=studID, list_of_files=list_of_files)

    # Retrieve the studentID from the query parameters
    studID = request.args.get('studentID')
    
    folder_name = 'Student/' + studID + "/" + "report/"

    # Uplaod image file in S3
    s3 = boto3.resource('s3')

    bucket = s3.Bucket(custombucket)
    list_of_files = list_files(bucket, folder_name)

    return render_template('report.html', my_bucket=bucket, studentID=studID, list_of_files=list_of_files)

# -------------------------------------------------------------- Student End --------------------------------------------------------------#


# -------------------------------------------------------------- Lecturer START (Kuah Jia Yu) --------------------------------------------------------------#

@app.route("/lectRegister", methods=['GET', 'POST'])
def lectRegister():
    if request.method == 'POST':
        lectName = request.form['lectName']
        lectID = request.form['lectID']
        lectEmail = request.form['lectEmail']
        gender = request.form['gender']
        password = request.form['password']

        insert_sql = "INSERT INTO lecturer VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        try:
            cursor.execute(insert_sql, (lectName,
                                        lectID,
                                        lectEmail,
                                        gender,
                                        password
                                        ))
            db_conn.commit()
            cursor.close()
            # Go to the dashboard after successful registration
            return redirect(url_for('login'))
        except Exception as e:
            cursor.close()
            return str(e)  # Handle any database errors here
    return render_template('lectRegister.html')


@app.route("/lectLogin", methods=['GET', 'POST'])
def lectLogin():
    if request.method == 'POST':
        return render_template('index.html', user_authenticated=True)

    # Fetch data from the database here
    cursor = db_conn.cursor()
    select_sql = "SELECT lectEmail, password FROM lecturer"
    cursor.execute(select_sql)
    data = cursor.fetchall()
    cursor.close()
    return render_template('lectLogin.html', lecturer=data)


@app.route("/lectDashboard", methods=['GET'])
def lectDashboard():
    return render_template('lectDashboard.html')

# ------------------------------------------------------------------- Lecturer END -------------------------------------------------------------------#

# ------------------------------------------------------------------- Company START (Wong Kar Yan) -------------------------------------------------------------------#

@app.route("/compRegister", methods=['GET', 'POST'])
def compRegister():
    if request.method == 'POST':
        compName = request.form['compName']
        compEmail = request.form['compEmail']
        comPassword = request.form['comPassword']
        companyImage = request.files['companyImage']

        # Check if the email is already in the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM company WHERE compEmail=%s", (compEmail))
        results = cursor.fetchall()
        cursor.close()

        # If the email is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('compRegister.html', email_error="This company email is already in use.")
        
        if companyImage.filename == "":
            return "Please select a file"
        
        insert_sql = "INSERT INTO company VALUES (%s, %s, %s)"
        cursor = db_conn.cursor()
        
        try:
            cursor.execute(insert_sql, (compName, 
                                        compEmail,
                                        comPassword
                                        ))
            db_conn.commit()
            cursor.close()

             # Uplaod image file in S3 #
            comp_image_file_name_in_s3 = "company-" + str(compName) + "_image_file"
            s3 = boto3.resource('s3')
        
            try:
                print("Data inserted in MySQL RDS... uploading image to S3...")
                s3.Bucket(custombucket).put_object(Key=comp_image_file_name_in_s3, Body=companyImage)
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3%7B0%7D.amazonaws.com/%7B1%7D/%7B2%7D".format(
                    s3_location,
                    custombucket,
                    comp_image_file_name_in_s3)
                return redirect(url_for('login'))  # Go to the dashboard after successful registration
            except Exception as e:
                cursor.close()
                print(f"Error during database insertion: {e}")
                return str(e)  # Handle any database errors here
                
        finally:
            cursor.close()
            
    return render_template('companyRegister.html')

@app.route("/jobReg", methods=['GET', 'POST'])
def jobReg():
    if request.method == 'POST':
        comp_name = request.form['comp_name']
        job_title = request.form['job_title']
        job_desc = request.form['job_desc']
        job_req = request.form['job_req']
        sal_range = request.form['sal_range']
        contact_person_name = request.form['contact_person_name']
        contact_person_email = request.form['contact_person_email']
        contact_number = request.form['contact_number']
        comp_state = request.form['comp_state']
        status = "pending"

        insert_sql = "INSERT INTO jobApply VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        cursor.execute(insert_sql, (comp_name, job_title, job_desc, job_req, sal_range, contact_person_name, contact_person_email, contact_number, comp_state,  status))
        db_conn.commit()
        cursor.close()

    return render_template('jobReg.html')


@app.route("/companyDashboard", methods=['GET'])
def companyDashboard():

    name = session.get('user_login_name', None)
    # Fetch job data from the database (assuming you have a SQL query for this)
    select_sql = "SELECT * FROM jobApply WHERE comp_name = %s"
    cursor = db_conn.cursor()
    cursor.execute(select_sql, (name,))
    job_data = cursor.fetchall()
    cursor.close()

    return render_template('companyDashboard.html', user_login_name=name, job_data=job_data)

@app.route('/jobDetail/<string:user_login_name>/<string:job_name>', methods=['GET'])
def job_details(user_login_name, job_name):
    
    # Fetch job details from the database using job_id
    cursor = db_conn.cursor()
    select_sql = "SELECT * FROM jobApply WHERE comp_name = %s AND job_title = %s"
    cursor.execute(select_sql, (user_login_name, job_name,))
    job_data = cursor.fetchone()
    cursor.close()
    
    #build the object key
    comp_image_file_name_in_s3 = "company-" + urllib.parse.quote_plus(user_login_name) + "_image_file"

    #generate the s3 url
    s3_url = "https://{0}.s3.amazonaws.com/{2}".format(custombucket, comp_image_file_name_in_s3)

    # Render the job details template and pass the job_data, job_name, and user_login_name
    return render_template('jobDetails.html', job_data=job_data, s3_url=s3_url)


# ------------------------------------------------------------------- Company END -------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)