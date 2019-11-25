from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from datetime import timedelta, datetime, tzinfo
import pymysql

app = Flask(__name__)
conn = pymysql.connect('localhost','root','','hrdb')

@app.route('/')
def hello():
        return render_template('index.html')

@app.route('/home')
def home():
        return render_template('index.html',) 

@app.route('/about-employee')
def about_employee():
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * from employee")
        rows_rs_employee = cur.fetchall()
        cur.execute("SELECT COUNT(emp_id) as count from employee")
        rows_count_employee = cur.fetchone()
        return render_template('about-employee.html',rs_employee=rows_rs_employee,count_employee=rows_count_employee)


@app.route('/about_us')
def about_us():
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * from employee_wage")
        rows = cur.fetchall()
        return render_template('about-us.html',datas=rows)


@app.route('/time_log')
def time_log():
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM employee_log_time LEFT JOIN employee_take_leave ON emptl_empid = empw_empid WHERE empw_date = CURDATE()")
        rows_rs_employee = cur.fetchall()
        cur.execute("SELECT DISTINCT empw_date FROM employee_log_time")
        rows_rs_date = cur.fetchall()
        times = ( timedelta(seconds=28800),timedelta(seconds=61200))
        return render_template('time-log.html',rows_rs_employee=rows_rs_employee,times=times,rows_rs_date=rows_rs_date)

@app.route('/calculate_salary')
def calculate_salary():
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * from employee_wage")
        rows = cur.fetchall()
        return render_template('calculate_salary.html',datas=rows)

@app.route('/employee_input')
def employee_input():
    return render_template('employee-input.html')

@app.route('/employee_insert',methods=['POST'])
def employee_insert():
    if request.method == "POST":
        emp_empid = request.form['emp_empid']
        emp_fname = request.form['emp_fname']
        emp_lname = request.form['emp_lname']
        emp_address = request.form['emp_address']
        emp_phone = request.form['emp_phone']
        with conn.cursor() as cur:
            sql="Insert into employee (emp_empid,emp_fname,emp_lname,emp_address,emp_phone) values(%s,%s,%s,%s,%s)"
            cur.execute(sql,(emp_empid,emp_fname,emp_lname,emp_address,emp_phone))
            conn.commit()
        return redirect(url_for('about_employee'))    

@app.route('/employee_delete/<string:id_data>',methods=['GET'])
def employee_delete(id_data):
    with conn.cursor() as cur:
        cur.execute("Delete from employee where emp_id = %s",(id_data))
        conn.commit()
    return redirect(url_for('about_employee'))    

if __name__ == "__main__":
    app.run(debug=True)