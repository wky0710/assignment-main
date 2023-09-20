from flask import Flask, render_template, request, redirect, url_for
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)
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
table = 'jobApply'

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
        
        insert_sql = "INSERT INTO students VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        
        try:
            cursor.execute(insert_sql, (email, 
                                        studentID, 
                                        firstName, 
                                        lastName, 
                                        gender,
                                        password,
                                        ic,
                                        programmeSelect,
                                        tutorialGrp,
                                        cgpa,
                                        ucSupervisor
                                        ))
            db_conn.commit()
            cursor.close()
            return redirect(url_for('login'))  # Redirect to the homepage after successful registration
        except Exception as e:
            cursor.close()
            return str(e)  # Handle any database errors here
    
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return render_template('index.html', user_authenticated=True)
    
    # Fetch data from the database here
    cursor = db_conn.cursor()
    select_sql = "SELECT email, password FROM students"
    cursor.execute(select_sql)
    data = cursor.fetchall()
    cursor.close()
    return render_template('login.html', students=data)

@app.route("/studentDashboard", methods=['GET'])
def studentDashboard():
    return render_template('studentDashboard.html')

@app.route("/form", methods=['GET'])
def form():
    return render_template('form.html')

@app.route("/report", methods=['GET'])
def report():
    return render_template('report.html')
    
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
                                        gender,
                                        password

                                        ))
            db_conn.commit()
            cursor.close()
            return redirect(url_for('login'))  # Go to the dashboard after successful registration
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

@app.route("/compRegister", methods=['GET', 'POST'])
def compRegister():
    if request.method == 'POST':
        compName = request.form['compName']
        compEmail = request.form['compEmail']
        comPassword = request.form['comPassword']

        insert_sql = "INSERT INTO company VALUES (%s, %s, %s)"
        cursor = db_conn.cursor()
        
        try:
            cursor.execute(insert_sql, (compName, 
                                        compEmail,
                                        comPassword
                                        ))
            db_conn.commit()
            cursor.close()
            return redirect(url_for('compLogin'))  # Go to the dashboard after successful registration
        except Exception as e:
            cursor.close()
            return str(e)  # Handle any database errors here
    return render_template('companyRegister.html')

@app.route("/compLogin", methods=['GET', 'POST'])
def compLogin():
    if request.method == 'POST':
        return render_template('index.html', user_authenticated=True)
    
    # Fetch data from the database here
    cursor = db_conn.cursor()
    select_sql = "SELECT compEmail, comPassword FROM company"
    cursor.execute(select_sql)
    data = cursor.fetchall()
    cursor.close()
    return render_template('compLogin.html', lecturer=data)

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
        companyImage = request.files['companyImage']

        insert_sql = "INSERT INTO jobApply VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        if companyImage.filename == "":
            return "Please select a file"
 
        cursor.execute(insert_sql, (comp_name, job_title, job_desc, job_req, sal_range, contact_person_name, contact_person_email, contact_number, comp_state))
        db_conn.commit()
        cursor.close()

        # Uplaod image file in S3 #
        comp_image_file_name_in_s3 = "company-" + str(comp_name) + "_image_file"
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
            return redirect(url_for('companyDashboard'))
        except Exception as e:
            cursor.close()
            print(f"Error during database insertion: {e}")
            return str(e)  # Handle any database errors here

    return render_template('jobReg.html')


@app.route("/companyDashboard", methods=['GET'])
def companyDashboard():
    return render_template('companyDashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)