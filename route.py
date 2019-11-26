from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify
from datetime import timedelta, datetime, tzinfo, date
import pymysql
import sys
#########################################################################################################################################################################
app = Flask(__name__)
#########################################################################################################################################################################
#config ฐานข้อมูล
conn = pymysql.connect('localhost','root','','hrdb')
#########################################################################################################################################################################
#หน้าแรก
@app.route('/')
def hello():
        return render_template('index.html')
#########################################################################################################################################################################
#หน้าหลัก
@app.route('/home')
def home():
        return render_template('index.html') 
#########################################################################################################################################################################
#หน้าข้อมูลพนักงาน
@app.route('/about-employee')
def about_employee():
    with conn.cursor() as cur:
        cur.execute("SELECT * from employee LEFT JOIN employee_department ON emp_empid = empdp_empid")
        rows_rs_employee = cur.fetchall()
        cur.execute("SELECT COUNT(emp_id) as count from employee")
        rows_count_employee = cur.fetchone()
    return render_template('about-employee.html',rs_employee=rows_rs_employee,count_employee=rows_count_employee)
#########################################################################################################################################################################
#หน้าเกี่ยวกับเรา
@app.route('/about_us')
def about_us():
    with conn.cursor() as cur:

        cur.execute("SELECT COUNT(emp_id) as count from employee")
        rows_count_employee = cur.fetchone()

        cur.execute("SELECT COUNT(SUBSTRING(emp_fname, 1, 3)) as prefix FROM employee WHERE SUBSTRING(emp_fname, 1, 3) = 'นาย'")
        rows_count_employee_male = cur.fetchone()

        cur.execute("SELECT COUNT(SUBSTRING(emp_fname, 1, 3)) as prefix FROM employee WHERE SUBSTRING(emp_fname, 1, 3) = 'น.ส'")
        rows_count_employee_female = cur.fetchone()

        cur.execute("SELECT COUNT(SUBSTRING(emp_fname, 1, 3)) as prefix FROM employee WHERE SUBSTRING(emp_fname, 1, 3) = 'นาง'")
        rows_count_employee_female2 = cur.fetchone()

    return render_template('about-us.html',count_employee=rows_count_employee,count_employee_male=rows_count_employee_male,count_employee_female=rows_count_employee_female,count_employee_female2=rows_count_employee_female2)
#########################################################################################################################################################################
#หน้าบันทึกเวลาเข้า-ออก
@app.route('/time_log')
def time_log():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM employee LEFT JOIN employee_log_time ON empw_empid = emp_empid WHERE empw_date = CURDATE()")
        rows_rs_employee = cur.fetchall()
        times = ( timedelta(seconds=28800),timedelta(seconds=61200))
    return render_template('time-log.html',rows_rs_employee=rows_rs_employee,times=times,cur_date=date.today())
#########################################################################################################################################################################
#หน้าบันทึกเวลาเข้า-ออก แบบค้นหาตามวันที่
@app.route('/time_log_search',methods=['POST'])
def time_log_search():
    empw_date = request.form['empw_date']
    with conn.cursor() as cur:

        cur.execute("SELECT * FROM employee LEFT JOIN employee_log_time ON empw_empid = emp_empid WHERE empw_date = %s",(empw_date))
        rows_rs_employee = cur.fetchall()

        times = ( timedelta(seconds=28800),timedelta(seconds=61200))

    return render_template('time-log.html',rows_rs_employee=rows_rs_employee,times=times,cur_date=empw_date)
#########################################################################################################################################################################
#หน้าคำนวณเงินเดือน
@app.route('/calculate_salary')
def calculate_salary():
    with conn.cursor() as cur:
        cur.execute("SELECT * from employee LEFT JOIN employee_department ON emp_empid = empdp_empid")
        rows_rs_employee = cur.fetchall()

        cur.execute("SELECT COUNT(emp_id) as count from employee")
        rows_count_employee = cur.fetchone()
    return render_template('calculate-salary.html',rs_employee=rows_rs_employee,count_employee=rows_count_employee)
#########################################################################################################################################################################
#ฟังก์ชันค้นหาวันที่ ของหน้าคำนวณเงินเดือน
@app.route('/calculate_salary_search',methods=['POST'])
def calculate_salary_search():
    if request.method == "POST":
        date_start = request.form['date_start']
        date_end = request.form['date_end']
        emp_empid = request.form['emp_empid']

        
        with conn.cursor() as cur:
            sql="SELECT SEC_TO_TIME( SUM( TIME_TO_SEC( `empt_hr` ) ) ) AS timeSum, SUM(empt_wage) as empt_wage from employee_wage LEFT JOIN employee_log_time ON empw_empid = empl_empid WHERE empt_date BETWEEN '"+date_start+"' AND '"+date_end+"' AND empw_empid = "+emp_empid+" GROUP BY empw_date"
            cur.execute(sql)
            rows_rs_wage = cur.fetchone()
            if rows_rs_wage == None:
                rows_rs_wage = "0";  
            cur.execute("SELECT empw_date, empw_time_in, empw_time_out,empw_sum_hr,empw_ot FROM employee LEFT JOIN employee_log_time ON empw_empid = emp_empid WHERE emp_empid = %s AND empw_date BETWEEN '"+date_start+"' AND '"+date_end+"' ORDER BY empw_date ASC",(emp_empid))
            rows_rs_timelog = cur.fetchall()
        return render_template('calculate-salary-search.html',rows_rs_wage=rows_rs_wage,rows_rs_timelog=rows_rs_timelog)
#########################################################################################################################################################################
#หน้าเพิ่มข้อมูลพนักงาน
@app.route('/employee_input')   
def employee_input():
    return render_template('employee-input.html')
#########################################################################################################################################################################
#ฟังก์ชันเพิ่มข้อมูลพนักงาน บันทึกลงฐานข้อมูล
@app.route('/employee_insert',methods=['POST'])
def employee_insert():
    if request.method == "POST":
        emp_empid = request.form['emp_empid']
        emp_fname = request.form['emp_fname']
        emp_lname = request.form['emp_lname']
        emp_address = request.form['emp_address']
        emp_phone = request.form['emp_phone']
        empdp_department = request.form['empdp_department']
        empdp_position = request.form['empdp_position']

        with conn.cursor() as cur:
            sql="Insert into employee (emp_empid,emp_fname,emp_lname,emp_address,emp_phone) values(%s,%s,%s,%s,%s)"
            cur.execute(sql,(emp_empid,emp_fname,emp_lname,emp_address,emp_phone))
            conn.commit()
            sql="Insert into employee_department (empdp_empid,empdp_department,empdp_position) values(%s,%s,%s)"
            cur.execute(sql,(emp_empid,empdp_department,empdp_position))
            conn.commit()
        return redirect(url_for('about_employee'))    
#########################################################################################################################################################################
#ฟังก์ชันลบข้อมูลพนักงาน ลบออกจากฐานข้อมูล
@app.route('/employee_delete/<string:empid>',methods=['GET'])
def employee_delete(empid):
    with conn.cursor() as cur:
        cur.execute("Delete from employee where emp_empid = %s",(empid))
        conn.commit()
        cur.execute("Delete from employee_department where empdp_empid = %s",(empid))
        conn.commit()
    return redirect(url_for('about_employee')) 
#########################################################################################################################################################################
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
        empdp_department = request.form['empdp_department']
        empdp_position = request.form['empdp_position']

        with conn.cursor() as cur:
            sql="UPDATE employee SET emp_empid=%s,emp_fname=%s,emp_lname=%s,emp_address=%s,emp_phone=%s WHERE emp_id = %s"
            cur.execute(sql,(emp_empid,emp_fname,emp_lname,emp_address,emp_phone,emp_id))
            conn.commit()

            sql="UPDATE employee_department SET empdp_empid=%s,empdp_department=%s,empdp_position=%s WHERE empdp_empid = %s"
            cur.execute(sql,(emp_empid,empdp_department,empdp_position,emp_empid))
            conn.commit()
        return redirect(url_for('about_employee'))  
#########################################################################################################################################################################
#หน้าเพิ่มข้อมูลพนักงาน
@app.route('/timelog_input')   
def timelog_input():
    with conn.cursor() as cur:
        cur.execute("SELECT emp_empid ,emp_fname ,emp_lname, empdp_department, empdp_position from employee LEFT JOIN employee_department ON empdp_empid = emp_empid")
        rows_rs_select_employee = cur.fetchall()
    return render_template('timelog-input.html',select_employee=rows_rs_select_employee)
#########################################################################################################################################################################
#ฟังก์ชันเพิ่มข้อมูลพนักงาน บันทึกลงฐานข้อมูล
@app.route('/timelog_insert',methods=['POST'])
def timelog_insert():
    if request.method == "POST":
        emp_empid = request.form['emp_empid']
        emp_name = request.form['emp_name']
        emp_date = request.form['emp_date']
        emp_time_in = request.form['emp_time_in']
        emp_time_out = request.form['emp_time_out']
        emp_code = request.form['emp_code']

        hour_in, minute_in = map(int, emp_time_in.split(':'))
        emp_time_in = timedelta(hours=hour_in, minutes =minute_in)
      
        hour_out, minute_out = map(int, emp_time_out.split(':'))
        emp_time_out = timedelta(hours=hour_out, minutes =minute_out)

        emp_sum_hr = emp_time_out - emp_time_in
        if emp_time_out >= timedelta(seconds=61200):
            emp_ot = emp_time_out - timedelta(seconds=61200)
        else:
            emp_ot = timedelta(seconds=0)

        emp_time_work = emp_sum_hr + emp_ot
        emp_wage = emp_time_work * 50

        with conn.cursor() as cur:
            sql="Insert into employee_log_time (empw_code,empw_empid,empw_name,empw_time_in,empw_time_out,empw_sum_hr,empw_ot,empw_date) values(%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sql,(emp_code,emp_empid,emp_name,emp_time_in,emp_time_out,emp_sum_hr,emp_ot,emp_date))
            conn.commit()

            sql="Insert into employee_wage (empt_no,empl_empid,empt_name,empt_hr,empt_wage,empt_date) values(%s,%s,%s,%s,%s,%s)"
            cur.execute(sql,(emp_code,emp_empid,emp_name,emp_time_work,emp_wage,emp_date))
            conn.commit()
        return redirect(url_for('time_log'))    
#########################################################################################################################################################################
if __name__ == "__main__":
    app.run(debug=True)
