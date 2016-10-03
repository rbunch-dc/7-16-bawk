# Import flask stuff
from flask import Flask, render_template, redirect, request
# Import the mysql module
from flaskext.mysql import MySQL

# Set up mysql connection here later
mysql = MySQL()
app = Flask(__name__)

# Add config data for mysql to connect
app.config['MYSQL_DATABASE_USER'] = 'x'
app.config['MYSQL_DATABASE_PASSWORD'] = 'x'
app.config['MYSQL_DATABASE_DB'] = 'bawk'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

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
		password = request.form['password'].encode('utf-8')
		hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
		username_insert_query = "INSERT INTO user VALUES ()"		
		conn.commit()
		return "You are logged in type page"
	else:
		return redirect('/register?username=taken')
	print check_username_result
	return "Done"
	# Second, if it is taken, send them back to the register page with a message
	# Second B, if it's not taken, then isert the user into mysql

@app('/login_submit', methods=['POST'])
def login_submit():
	# To check a hash against english:
	if bcrypt.hashpw(password.encode('utf-8'), hashsed_passwrod_from_mysql) == hashsed_passwrod_from_mysql:
		# We have a match

if __name__ == "__main__":
	app.run(debug=True)