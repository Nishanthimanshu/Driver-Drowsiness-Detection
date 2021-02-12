import re
import drowsiness
import MySQLdb.cursors
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from flask_mysqldb import MySQL
from drowsiness import VideoCamera
app= Flask(__name__)

app.secret_key = '1a2b3c4d5e'
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = '8lMAr0y3ft'
app.config['MYSQL_PASSWORD'] = 'EqfKP92zZM'
app.config['MYSQL_DB'] = '8lMAr0y3ft'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/login', methods=['GET','POST'])
def login():
	msg=''
	if request.method=='POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']

		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("""SELECT * FROM `pythonlogin` WHERE `username` LIKE '{}' AND `password` LIKE '{}'""".format(username, password))
		# Fetch one record and return result
		account = cursor.fetchone()
		# If account exists in accounts table in out database
		if account:
			# Create session data, we can access this data in other routes
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			# Redirect to home page
			return redirect(url_for('home'))
		else:
			# Account doesnt exist or username/password incorrect
			msg = 'Incorrect username/password!'
	return render_template('index.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():

	msg=''
	if request.method=='POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
		username=request.form.get('username')
		password=request.form.get('password')
		email=request.form.get('email')

		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("""SELECT * FROM `pythonlogin` WHERE `username` LIKE '{}'""".format(username))
		account = cursor.fetchone()
		# If account exists show error and validation checks
		if account:
			msg = 'Account already exists!'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address!'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers!'
		elif not username or not password or not email:
			msg = 'Please fill out the form!'
		else:
			# Account doesnt exists and the form data is valid, now insert new account into accounts table
			cursor.execute("""INSERT INTO `pyhtonlogin` VALUES(NULL,'{}','{}','{}')""".format(username, password, email))
			mysql.connection.commit()
			msg = 'You have successfully registered!'
	elif request.method=='POST':
		msg='Please fill out the form!'

	return render_template('register.html', msg=msg)


@app.route('/')
def index():
	if request.method == 'GET':
		if 'user_id' in session:
			return redirect(url_for('home'))
	return redirect(url_for('login'))


@app.route('/home')
def home():
	if 'loggedin' in session:
		return render_template('home.html', username=session['username'])

	return redirect(url_for('login'))

@app.route('/logout')
def logout():
	session.pop('user_id', None)
	flash('You have successfully logged out.')
	return redirect('/login')

@app.route('/ddd')
def ddd():
	return render_template("ddd.html")
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=='__main__':
	app.run(debug=True, port=5000)
