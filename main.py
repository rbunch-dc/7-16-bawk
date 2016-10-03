# Import flask stuff
from flask import Flask, render_template, redirect, request, session
# Import the mysql module
from flaskext.mysql import MySQL
import bcrypt

# Set up mysql connection here later
mysql = MySQL()
app = Flask(__name__)

# Add config data for mysql to connect
app.config['MYSQL_DATABASE_USER'] = 'x'
app.config['MYSQL_DATABASE_PASSWORD'] = 'x'
app.config['MYSQL_DATABASE_DB'] = 'bawk'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

# Secret key for session
app.secret_key = 'HSDG#$%T34t35t3tREGgfsDG34t34543t3455fdsfgdfsgd'

#Make one connection and use it over, and over, and over...
conn = mysql.connect()
# set up a cursor object whihc is what the sql object uses to connect and run queries
cursor = conn.cursor()


# Create route for home page
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/register')
def register():
	if request.args.get('username'):
		# the username variable is set in the query string.
		return render_template('register.html',
			message = "That username is already taken.")
	else:
		return render_template('register.html')

@app.route('/register_submit', methods=['POST'])
def register_submit():
	# First, check to see if the username is already taken.
	# THis means a select statement.
	check_username_query = "SELECT * FROM user WHERE username = '%s'" % request.form['user_name']

	# print check_username_query
	cursor.execute(check_username_query)
	check_username_result = cursor.fetchone()
	if check_username_result is None:
		# No match. Insert
		real_name = request.form['name']
		user_name = request.form['user_name']
		email = request.form['email']
		password = request.form['password'].encode('utf-8')
		hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
		print "---------------"
		print hashed_password
		username_insert_query = "INSERT INTO user (real_name, username, password, email) VALUES ('"+real_name+"', '"+user_name+"', '"+hashed_password+"', '"+email+"')"		
		cursor.execute(username_insert_query)
		conn.commit()
		return "You are logged in type page"
	else:
		return redirect('/register?username=taken')
	print check_username_result
	return "Done"
	# Second, if it is taken, send them back to the register page with a message
	# Second B, if it's not taken, then isert the user into mysql

@app.route('/login')
def login():
	return render_template('login.html')


@app.route('/login_submit', methods=['POST'])
def login_submit():
	check_username_query = "SELECT password FROM user WHERE username = '%s'" % request.form['username']
	cursor.execute(check_username_query)
	check_username_result = cursor.fetchone()
	password = request.form['password'].encode('utf-8')
	hashsed_password = check_username_result[0].encode('utf-8')
	if check_username_result is not None:
		print '----------------'
		print check_username_result[0]
		# To check a hash against english:
		if bcrypt.hashpw(password, hashsed_password) == hashsed_password:
			# We have a match
			session['username'] = request.form['username']
			return render_template('index.html')
		else:
			return redirect('/login',
				message = "password=wrong"
			)
	else:
		return redirect('/login',
			message = "username=missing"
		)

@app.route('/logout')
def logout():
	# Nuke their session vars. This will end the session which is waht we use to let them into the portal
	session.clear()	
	return redirect('/?message=LoggedOut')


if __name__ == "__main__":
	app.run(debug=True)