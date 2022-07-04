
from cgitb import html
from fileinput import filename
from argon2 import hash_password
import cursor
from flask import Flask, render_template, request, redirect, url_for, flash, session
import bcrypt
import pymysql
from flask_session import Session
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET_KEY"

host = "localhost"
user = "root"
password_db = ""
database = "donausguard"


@app.route("/")
def login():
    return render_template("login.html")

@app.route("/confirm_delete")
def confirm_delete():
    return render_template("confirm_delete.html")


@app.route("/home")
def home():
    connection = pymysql.connect(host=host, user=user,passwd=password_db,database=database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM data_config")
    data = cursor.fetchall()
    connection.close()
    return render_template("index.html", data_config=data)


@app.route("/admin")
def admin():
    connection = pymysql.connect(host=host, user=user,passwd=password_db,database=database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    connection.close()
    return render_template("admin.html", users=data)


@app.route('/insert_config', methods=['POST', 'GET'])
def insert_config():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        email = request.form['email']
        connection = pymysql.connect(host=host, user=user,passwd=password_db,database=database)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s",(username,))
        data = cursor.fetchone()
        if data is not None and len(data) > 0:
            return render_template('register_error.html')
        cursor.execute("INSERT INTO users (username,password,email) VALUES (%s,%s,%s)", (username, hash_password, email,))
        connection.commit()
        cursor.close()
        return render_template('register_success.html')


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        LineliffID = request.form['LineliffID']
        Even = request.form['Even']
        CamID = request.form['CamID']
        IFTTTkey = request.form['IFTTTkey']
        Location = request.form['Location']
        connection = pymysql.connect(host=host, user=user,passwd=password_db,database=database)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO data_config (lineliff_id,even,cam_id,ifttt_key,location) VALUES (%s,%s,%s,%s,%s)", (LineliffID, Even, CamID, IFTTTkey, Location))
        connection.commit()
        connection.close()
        flash("บันทึกข้อมูลสำเร็จ","success")
        return redirect("/home")


@app.route('/add_user', methods=['POST', 'GET'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        email = request.form['email']
        connection = pymysql.connect(host=host, user=user, passwd=password_db,database=database)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s",(username,))
        data = cursor.fetchone()
        if data is not None and len(data) > 0:
            flash("มีผู้ใช้นี้แล้ว","danger")
            return redirect("/admin")
        cursor.execute("INSERT INTO users (username,password,email) VALUES (%s,%s,%s)", (username, hash_password, email))
        connection.commit()
        connection.close()
        flash("บันทึกข้อมูลสำเร็จ","success")
        return redirect("/admin")


@app.route('/update_config', methods=['POST', 'GET'])
def update_config():
    if request.method == 'POST':
        id = request.form['id']
        LineliffID = request.form['LineliffID']
        Even = request.form['Even']
        CamID = request.form['CamID']
        IFTTTkey = request.form['IFTTTkey']
        Location = request.form['Location']
        connection = pymysql.connect(host=host, user=user,passwd=password_db,database=database)
        cursor = connection.cursor()
        cursor.execute("UPDATE data_config SET lineliff_id=%s, even=%s, cam_id=%s, ifttt_key=%s, location=%s WHERE id=%s ",
                       (LineliffID, Even, CamID, IFTTTkey, Location, id))
        cursor = connection.cursor()
        connection.commit()
        connection.close()
        flash("อัพเดทข้อมูลสำเร็จ","success")
        return redirect("/home")


@app.route('/update_user', methods=['POST', 'GET'])
def update_user():
    if request.method == 'POST':
        id = request.form['id']
        username = request.form['username']
        email = request.form['email']
        connection = pymysql.connect(host=host, user=user,passwd=password_db,database=database)
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET username=%s, email=%s  WHERE id=%s", (username, email, id))
        cursor = connection.cursor()
        connection.commit()
        connection.close()
        flash("อัพเดทข้อมูลสำเร็จ","success")
        return redirect("/admin")


@app.route('/delete_config/<string:id>', methods=['POST', 'GET'])
def delete_config(id):
    connection = pymysql.connect(host=host, user=user,passwd=password_db,database=database)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM data_config WHERE id=%s ", [id])
    connection.commit()
    connection.close()
    flash("ลบข้อมูลสำเร็จ","success")
    return redirect("/home")


@app.route('/delete_user/<string:id>', methods=['POST', 'GET'])
def delete_user(id):
    connection = pymysql.connect(host=host, user=user,passwd=password_db,database=database)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s ", [id])
    connection.commit()
    connection.close()
    flash("ลบข้อมูลสำเร็จ","success")
    return redirect("/admin")


@app.route('/login_system', methods=['GET', 'POST'])
def login_system():
    if request.method == 'POST':
        _username = request.form['username']
        _password = request.form['password'].encode('utf-8')
        connection = pymysql.connect(host=host, user=user,passwd=password_db,database=database)
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username=%s",(_username,))
        data = cursor.fetchone()
        cursor.close()
        if data is not None and len(data) > 0:
            if bcrypt.hashpw(_password, data['password'].encode('utf-8')) == data['password'].encode('utf-8'):
                session['username'] = data['username']
                session['_password'] = data['password']
                return render_template('login_success.html', _username = _username)
            else:
                return render_template('login_error.html')
        else:
            return render_template('login_error.html')
    else:
        return render_template('login_error.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True, use_reloader=True)
