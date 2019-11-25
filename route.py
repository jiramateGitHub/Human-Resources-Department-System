from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify
from datetime import timedelta, datetime, tzinfo, date
import pymysql
import json

app = Flask(__name__)

#config ฐานข้อมูล
conn = pymysql.connect('localhost','root','','hrdb')

#หน้าแรก
@app.route('/')
def hello():
        return render_template('index.html')

#หน้าหลัก
@app.route('/home')
def home():
        return render_template('index.html',) 

#หน้าข้อมูลพนักงาน
@app.route('/about-employee')
def about_employee():
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * from employee")
        rows_rs_employee = cur.fetchall()
        cur.execute("SELECT COUNT(emp_id) as count from employee")
        rows_count_employee = cur.fetchone()
        return render_template('about-employee.html',rs_employee=rows_rs_employee,count_employee=rows_count_employee)

#หน้าเกี่ยวกับเรา
@app.route('/about_us')
def about_us():
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(emp_id) as count from employee")
        rows_count_employee = cur.fetchone()
        cur.execute("SELECT COUNT(SUBSTRING(emp_fname, 1, 3)) as prefix FROM employee WHERE SUBSTRING(emp_fname, 1, 3) = 'นาย'")
        rows_count_employee_male = cur.fetchone()
        cur.execute("SELECT COUNT(SUBSTRING(emp_fname, 1, 3)) as prefix FROM employee WHERE SUBSTRING(emp_fname, 1, 3) = 'น.ส'")
        rows_count_employee_female = cur.fetchone()
        cur.execute("SELECT COUNT(SUBSTRING(emp_fname, 1, 3)) as prefix FROM employee WHERE SUBSTRING(emp_fname, 1, 3) = 'นาง'")
        rows_count_employee_female2 = cur.fetchone()
        return render_template('about-us.html',count_employee=rows_count_employee,count_employee_male=rows_count_employee_male,count_employee_female=rows_count_employee_female,count_employee_female2=rows_count_employee_female2)

#หน้าบันทึกเวลาเข้า-ออก
@app.route('/time_log')
def time_log():
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM employee_log_time LEFT JOIN employee_take_leave ON emptl_empid = empw_empid WHERE empw_date = CURDATE()")
            rows_rs_employee = cur.fetchall()
            cur.execute("SELECT DISTINCT empw_date FROM employee_log_time")
            rows_rs_date = cur.fetchall()
            times = ( timedelta(seconds=28800),timedelta(seconds=61200))
        return render_template('time-log.html',rows_rs_employee=rows_rs_employee,times=times,rows_rs_date=rows_rs_date,cur_date=date.today(),select_cur_date=date.today())

#หน้าบันทึกเวลาเข้า-ออก แบบค้นหาตามวันที่
@app.route('/time_log_search',methods=['POST'])
def time_log_search():
        empw_date = request.form['empw_date']
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM employee_log_time LEFT JOIN employee_take_leave ON emptl_empid = empw_empid WHERE empw_date = %s",(empw_date))
            rows_rs_employee = cur.fetchall()
            cur.execute("SELECT DISTINCT empw_date FROM employee_log_time")
            rows_rs_date = cur.fetchall()
            times = ( timedelta(seconds=28800),timedelta(seconds=61200))
        return render_template('time-log.html',rows_rs_employee=rows_rs_employee,times=times,rows_rs_date=rows_rs_date,cur_date=empw_date,select_cur_date=date.today())

#หน้าคำนวณเงินเดือน
@app.route('/calculate_salary')
def calculate_salary():
     with conn:
        cur = conn.cursor()
        cur.execute("SELECT * from employee LEFT JOIN employee_department ON empdp_empid = emp_empid")
        rows_rs_employee = cur.fetchall()
        cur.execute("SELECT COUNT(emp_id) as count from employee")
        rows_count_employee = cur.fetchone()
        return render_template('calculate-salary.html',rs_employee=rows_rs_employee,count_employee=rows_count_employee)
        

#ฟังก์ชันค้นหาวันที่ ของหน้าคำนวณเงินเดือน
@app.route('/calculate_salary_search',methods=['POST'])
def calculate_salary_search():
    if request.method == "POST":
        date_start = request.form['date_start']
        date_end = request.form['date_end']
        emp_empid = request.form['emp_empid']
        with conn:
            cur = conn.cursor()
            sql="SELECT SUM(empt_wage) as empt_wage,  DATEADD(ms, SUM(DATEDIFF(ms, '00:00:00.000', empt_hr)), '00:00:00.000') as time   from employee LEFT JOIN employee_department ON empdp_empid = emp_empid LEFT JOIN employee_wage ON empl_empid = emp_empid LEFT JOIN employee_log_time ON empw_empid = empl_empid WHERE empt_date BETWEEN '"+date_start+"' AND '"+date_end+"' AND emp_empid = %s"
            cur.execute(sql,(emp_empid))
            result = cur.fetchall()
            return render_template('calculate-salary-search.html',result=result)

#หน้าเพิ่มข้อมูลพนักงาน
@app.route('/employee_input')   
def employee_input():
    return render_template('employee-input.html')

#ฟังก์ชันเพิ่มข้อมูลพนักงาน บันทึกลงฐานข้อมูล
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

#ฟังก์ชันลบข้อมูลพนักงาน ลบออกจากฐานข้อมูล
@app.route('/employee_delete/<string:id_data>',methods=['GET'])
def employee_delete(id_data):
    with conn.cursor() as cur:
        cur.execute("Delete from employee where emp_id = %s",(id_data))
        conn.commit()
    return redirect(url_for('about_employee')) 

#ฟังก์ชันแก้ไขข้อมูลพนักงาน บันทึกลงฐานข้อมูล
@app.route('/employee_update',methods=['POST'])
def employee_update():
    if request.method == "POST":
        emp_id = request.form['emp_id']
        emp_empid = request.form['emp_empid']
        emp_fname = request.form['emp_fname']
        emp_lname = request.form['emp_lname']
        emp_address = request.form['emp_address']
        emp_phone = request.form['emp_phone']
        with conn.cursor() as cur:
            sql="UPDATE employee SET emp_empid=%s,emp_fname=%s,emp_lname=%s,emp_address=%s,emp_phone=%s WHERE emp_id = %s"
            cur.execute(sql,(emp_empid,emp_fname,emp_lname,emp_address,emp_phone,emp_id))
            conn.commit()
        return redirect(url_for('about_employee'))  

if __name__ == "__main__":
    app.run(debug=True)
