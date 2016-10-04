# Import flask stuff
from flask import Flask, render_template, redirect, request, session, jsonify
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
	get_bawks_query = "SELECT b.id, b.post_content, b.current_vote, b.timestamp, u.username, b.current_vote FROM bawks AS b INNER JOIN user u ON b.uid = u.id WHERE 1"
	cursor.execute(get_bawks_query)
	get_bawks_result = cursor.fetchall()
	if get_bawks_result is not None:
		return render_template('index.html', bawks = get_bawks_result)
	else:
		return render_template('index.html', message = "No bawks yet!")

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
		# print "---------------"
		# print hashed_password
		username_insert_query = "INSERT INTO user (real_name, username, password, email) VALUES ('"+real_name+"', '"+user_name+"', '"+hashed_password+"', '"+email+"')"		
		cursor.execute(username_insert_query)
		conn.commit()
		session['username'] = user_name
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
	check_username_query = "SELECT password, id FROM user WHERE username = '%s'" % request.form['username']
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
			session['id'] = check_username_result[1]
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

@app.route('/post_submit', methods=["POST"])
def post_submit():
	post_content = request.form['post_content']
	get_user_id_query = "SELECT id FROM user WHERE username = '%s'" %session['username']
	cursor.execute(get_user_id_query)
	get_user_id_result = cursor.fetchone()
	user_id = get_user_id_result[0]

	insert_post_query = "INSERT INTO bawks (post_content, uid, current_vote) VALUES ('"+post_content+"', "+str(user_id)+", 0)"
	cursor.execute(insert_post_query)
	conn.commit()
	return redirect('/')

@app.route('/process_vote', methods=['POST'])
def process_vote():
	# check to see, has th euser voted on this particular item
	pid = request.form['vid'] # the post they voted on. This came from jquery $.ajax
	vote_type = request.form['voteType']
	check_user_votes_query = "SELECT * FROM votes INNER JOIN user ON user.id = votes.uid WHERE user.username = '%s' AND votes.pid = '%s'" % (session['username'], pid)
	# print check_user_votes_query
	cursor.execute(check_user_votes_query)
	check_user_votes_result = cursor.fetchone()

	# It's possible we get None back, becaues the user hsn't voted on this post
	if check_user_votes_result is None:
		# User hasn't voted. Insert.
		insert_user_vote_query = "INSERT INTO votes (pid, uid, vote_type) VALUES ('"+str(pid)+"', '"+str(session['id'])+"', '"+str(vote_type)+"')"
		# print insert_user_vote_query
		cursor.execute(insert_user_vote_query)
		conn.commit()
		return jsonify("voteCounted")
	else:
		check_user_vote_direction_query = "SELECT * FROM votes INNER JOIN user ON user.id = votes.uid WHERE user.username = '%s' AND votes.pid = '%s' AND votes.vote_type = %s" % (session['username'], pid, vote_type)
		cursor.execute(check_user_vote_direction_query)
		check_user_vote_direction_result = cursor.fetchone()
		if check_user_vote_direction_result is None:
			# User has voted, but not this direction. Update
			update_user_vote_query = "UPDATE votes SET vote_type = %s WHERE uid = '%s' AND pid = '%s'" % (vote_type, session['id'], pid)
			cursor.execute(update_user_vote_query)
			conn.commit()
			return "voteChanged"
		else:
			# User has already voted this directino on this post. No dice.
			return "alreadyVoted"

if __name__ == "__main__":
	app.run(debug=True)