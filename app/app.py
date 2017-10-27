
from flask import Flask ,render_template, flash, redirect, url_for, session, request, logging
from functools import wraps
import dbquery
app = Flask(__name__,static_url_path='/static' )

@app.route('/')
def index():
     return render_template('index.html')

@app.route('/login', methods=['GET','POST']) #login page
def login():
	if request.method == 'POST':
		email = request.form['email']					#GET FORM FIELDS
		password_candidate= request.form['password']	#GET FORM FIELDS
		flag=0
		if email=='admin@mindhacks.com':
			if password_candidate=='adminadmin':
				session['logged_in'] = True
				session['name'] = 'Administrator'
				session['userid']='0'
				return render_template('admin_dash.html')


		sql="SELECT PASSWORD FROM USERS WHERE EMAIL= '%s' "%(email)
		rows = dbquery.fetchone(sql)
		try:				# if no entry found, an error is raised
			for row in rows:
				flag=1
				password=row
			sql="SELECT NAME FROM USERS WHERE EMAIL= '%s' "%(email)		#validations
			rows = dbquery.fetchone(sql)
			for row in rows:
				name=row
			sql="SELECT USERID FROM USERS WHERE EMAIL= '%s' "%(email)	#validations
			rows = dbquery.fetchone(sql)
			for row in rows:
				userid=row
			sql="SELECT CITY FROM USERS WHERE EMAIL= '%s' "%(email)	
			rows = dbquery.fetchone(sql)
			for row in rows:
				city=row
			if str(password_candidate) == str(password):	#initialise session variable if passwords match
				session['logged_in'] = True
				session['name'] = str(name)
				session['userid']=userid
				session['city']=city
                
			else:
				error = 'Invalid login'
				return render_template('login.html',error=error)
		except:
			if flag==0:
				error = 'Email not found'
				return render_template('login.html',error=error)
		return redirect( url_for('dashboard'))#if verification is successful load the dashboard with session
	return render_template('login.html')


def is_logged_in(f):	# Function for implementing security and redirection
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorised, Please Login')
			return redirect(url_for('login'))
	return wrap	# A wrap is a concept that is used to check for authorisation of a request

@app.route('/dashboard',methods=['GET','POST'])
@is_logged_in	
def dashboard():
	city=session['city']	#Recieving the userid for db manipulation from the initilised session
	sql="SELECT * FROM USERS WHERE CITY = '%s' AND USERID <> %d"%(city,session['userid'])
	people=dbquery.fetchall(sql)
	return render_template('dashboard.html',people=people)




@app.route('/signup',methods=['GET','POST'])
def signup():
	if request.method== 'POST': #retrieving values from user if POST
		name = request.form['name']
		email = request.form['email']
		password= request.form['password']
		country=request.form['country']
		country=country.lower()
		city=request.form['city']
		city=city.lower()
		sql="SELECT USERID FROM USERS WHERE EMAIL='%s'"%(email) #Security check on email
		try:
			rows = dbquery.fetchone(sql) #if none, error should be raised
			for row in rows:
				f=1
		except:
			sql="INSERT INTO USERS(NAME,EMAIL,PASSWORD,COUNTRY,CITY) VALUES('%s','%s' ,'%s','%s','%s')"%(name,email,password,country,city)
			dbquery.inserttodb(sql)	#connecting to db model
			flash('You are now registered! Please Log in.','success') #sending a message to user
			return redirect( url_for('login')) #redirecting to login page
		flash('This Email exists!','success') #Checking for email
		return render_template('signup.html')
	return render_template('signup.html') # rendering the signup page


@app.route('/chat/<int:id>',methods=['GET','POST'])
def projects(id):
    if id == session['userid']:
    		return redirect(url_for('dashboard'))
	if request.method=='POST':
		message=request.form['message']
		name =str(session['name'])
		message=name+": "+message
		sql="INSERT INTO CHATS(SENDER,RECIEVER,MESSAGE) VALUES('%d','%d','%s')"%(session['userid'],id,message)
		dbquery.inserttodb(sql)
		sql="SELECT MESSAGE FROM CHATS WHERE (SENDER = %d AND RECIEVER = %d) OR (SENDER= %d AND RECIEVER = %d) "%(session['userid'],id,id,session['userid'])
		chats=dbquery.fetchall(sql)


		return render_template("chat.html",chats=chats)

	try:
		sql="SELECT MESSAGE FROM CHATS WHERE (SENDER = %d AND RECIEVER = %d) OR (SENDER= %d AND RECIEVER = %d) "%(session['userid'],id,id,session['userid'])
		chats=dbquery.fetchall(sql)
		return render_template("chat.html",chats=chats)
	except:
		sql="INSERT INTO CHATS(SENDER,RECIEVER,MESSAGE) VALUES('%d','%d','%s')"%(session['userid'],id,"Say hello")
		dbquery.inserttodb(sql) 
		sql="SELECT MESSAGE FROM CHATS WHERE (SENDER = %d AND RECIEVER = %d) OR (SENDER= %d AND RECIEVER = %d) "%(session['userid'],id,id,session['userid'])
		chats=dbquery.fetchall(sql)
		return render_template("chat.html",chats=chats)

#------------------------------logout function----------------------------------
@app.route('/logout')
def logout():
	session.clear()								#Session is destroyed
	flash('You are now logged out','success')
	return redirect(url_for('index'))

app.secret_key='secret123'
app.run(host = '0.0.0.0',port=80,threaded=True)
