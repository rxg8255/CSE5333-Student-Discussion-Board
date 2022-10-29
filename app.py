from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = '<SERVERNAME OR IP>'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '<PASSWORD>'
app.config['MYSQL_DB'] = '<DBNAME>'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        conn.execute("SELECT * FROM accounts WHERE userid = '{}' AND password ='{}'".format(userid, password, ))
        account = conn.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['userid']
            session['type'] = account['user_type']
            msg = 'Logged in successfully !'
            return redirect(url_for('inventory', msg=msg))
        else:
            msg = 'Incorrect username / password !'
            return render_template('login.html', msg=msg)
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('type', None)
    return redirect(url_for('login'))

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    msg = ''
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        email = request.form['email']
        usertype = request.form['usertype']
        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        conn.execute('SELECT * FROM accounts WHERE userid = % s', (userid,))
        account = conn.fetchone()
        if account:
            msg = 'Account already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address'
        elif not userid or not password or not email:
            msg = 'Please fill all details'
        else:
            conn.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s)', (userid, password, email, usertype,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            return render_template('login.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)

@app.route('/posts', methods=['GET', 'POST'], defaults={'opt': None})
def inventory(opt):
    msg = ''
    if session['loggedin']:
        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        conn.execute('SELECT * FROM posts')
        posts = conn.fetchall()
        return render_template('posts.html', posts=posts)
    else:
        msg = 'Error loading Books, please try again'
        return render_template('login.html', msg=msg)