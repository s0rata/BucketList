from flask import Flask, render_template, request, json, url_for, flash, redirect, session 
from flask.ext.mysql import MySQL 
from werkzeug import generate_password_hash, check_password_hash
import os
import uuid

app = Flask(__name__)
mysql = MySQL()

# Default Setting
pageLimit = 2
# flash configuration
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
# MySQL configuration
app.config['MYSQL_DATABASE_USER'] ='root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'ichigo.15'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
# Default upload folder
app.config['UPLOAD_FOLDER'] = 'static/Uploads'


@app.route('/')
@app.route('/home')
def index():
	if session.get('user_id'):
		return redirect('/dashboard')
	else:
		return render_template('index.html')


@app.route('/signup', methods = ['GET', 'POST'])
def signup(message='', alert='', error=''):
	if request.method == 'GET':
		return render_template('signup.html')
	elif request.method =='POST':
		# read data from form
		Name = request.form['name']
		Username = request.form['username']
		Password = request.form['password']
		# validate data with json
		if Name and Username and Password:
			conn = mysql.connect()
			cur = conn.cursor()
			HashPassword = generate_password_hash(Password, method= "pbkdf2:sha1",salt_length = 7)
			cur.callproc('sp_createUser', (Name, Username, HashPassword))
			data = cur.fetchall()
			if len(data) is 0:
				conn.commit()
				alert = 'alert-success'
				error = 'Success'
				message = 'User created successfully'
				# flash(message)
				# return json.dumps({'message':'User created successfully'})
				return render_template('signup.html', message=message, error=error, alert=alert)
			else:
				# return json.dumps({'error': str(data[0])})
				alert = 'alert-danger'
				error = 'Error'
				message = 'Username already exist'
				return render_template('signup.html', message=message, error=error, alert=alert)
			cur.close()
			conn.close()
		return render_template('signup.html')

@app.route('/signin', methods = ['GET', 'POST'])
def signin(message='', alert='', error=''):
	if request.method == 'GET':
		return render_template('login.html')
	elif request.method == 'POST':
		try:
			Username = request.form['username']
			Password = request.form['password']
		except Exception as e:
			return render_template('error.html', error = str(e))

		if Username and Password:
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.callproc('sp_validateLogin',(Username,))
			data = cursor.fetchall()
			if len(data) > 0:
				if check_password_hash(str(data[0][3]),Password):
					alert = 'alert-success'
					error = 'Success'
					message = 'User logged in successfully'
					session['user_id']=data[0][0]
					session['user']=data[0][1]
					#return render_template('user.html', alert = alert, error = error, message = message, user = data[0][0])
					return redirect('/dashboard')
					# return json.dumps({'message':'success'})
				else:
					alert = 'alert-danger'
					error = 'Error'
					message = 'Wrong username or password'
					return render_template('login.html', message = message, error = error, alert = alert)
			else:
				alert = 'alert-danger'
				error = 'Error'
				message = 'Wrong username or password'
				return render_template('login.html', message = message, error = error, alert = alert)
			cursor.close()
			conn.close()
	return render_template('login.html')

@app.route('/userHome/')
def userHome():
	if session.get('user_id'):
		user = session.get('user')
		return render_template('user.html', user=user, conent = "None")
	else:
		return render_template('error.html', error = 'Unauthorized Access')

@app.route('/logout')
def logout():
	session.pop('user_id', None)
	return redirect('/')

@app.route('/addWish', methods=['POST', 'GET'])
def addWish():
	if request.method == "GET":
		return render_template('addWish.html')
	elif request.method == 'POST':
		try:
			if session.get('user_id'):
				Title = request.form['txtTitle']
				Description = request.form['txtDescription']
				User = session.get('user_id')
				print request.form.get('filePath')
				if request.form.get('filePath') is None:
					FilePath = ''
				else:
					FilePath = request.form.get('filePath')
				if request.form.get('private') is None:
					Private = 0
				else:
					Private = 1
				if request.form.get('done') is None:
					Done = 0
				else:
					Done = 1

				conn = mysql.connect()
				cursor = conn.cursor()
				cursor.callproc('sp_addWish', (Title, Description, User, FilePath, Private, Done))
				data = cursor.fetchall()

				if len(data) is 0:
					conn.commit()
					return redirect('/userHome')
				else:
					return render_template('error.html', error = 'An error occured!')
			else:
				return render_template('error.html', error = 'Unauthorized Access')
		except Exception as e:
			return render_template('error.html', error = str(e))
		finally:
			cursor.close()
			conn.close()

@app.route('/getWish', methods = ['POST'])
def getWish():
	try:
		if session.get('user_id'):
			User = session.get('user_id')
			Limit = pageLimit
			Offset = request.form['offset']
			TotalRecords = 0

			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.callproc('sp_getUserWish', (User, Limit, Offset, TotalRecords))
			wishes = cursor.fetchall()
			cursor.close()

			cursor = conn.cursor()
			cursor.execute('SELECT @_sp_getUserWish_3');
			outParam = cursor.fetchall()

			response = []
			wishes_dict = []

			for wish in wishes:
				wish_dict = {
					'Id': wish[0],
					'Title': wish[1],
					'Description': wish[2],
					'Date': wish[4]}
				wishes_dict.append(wish_dict)

			response.append(wishes_dict)
			response.append({'total':outParam[0][0]})
			return json.dumps(response)
		else:
			return render_template('error.html', error = 'Unauthorized Access')
	except Exception as e:
		return render_template('error.html', error = str(e))

@app.route('/getWishById', methods = ['POST'])
def getWishById():
	try:
		if session.get('user_id'):
			
			Id = request.form['id']
			User = session.get('user_id')
			
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.callproc('sp_getWishById', (Id,User))
			result = cursor.fetchall()
			# print result
			wish = []
			wish.append({'Id':result[0][0],'Title':result[0][1],'Description':result[0][2], 'FilePath':result[0][3], 'Private': result[0][4], 'Done': result[0][5]})
			# print wish
			return json.dumps(wish)
		else:
			return render_template('error.html', error = 'Unauthorized Access')
	except Exception as e:
		return render_template('error.html', error = str(e))
	finally:
		cursor.close()
		conn.close()

@app.route('/updateWish', methods = ['POST'])
def updateWish():
	try:
		if session.get('user_id'):

			Title = request.form['title']
			Description = request.form['description']
			User = session.get('user_id')
			Id = request.form['id']
			FilePath = request.form['filePath']
			Private = request.form['isPrivate']
			Done = request.form['isDone']
			# print FilePath, Private, Done
			
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.callproc('sp_updateWish', (Id, User, Title, Description, FilePath, Private, Done))
			data = cursor.fetchall()
			# print data
			if len(data) is 0:
				conn.commit()
				return json.dumps({'Status':'Ok'})
			else:
				return json.dumps({'Status': 'Error'})
	except Exception as e:	
		return json.dumps({'Status':'Unauthorized Access'})
	finally:
		cursor.close()
		conn.close()

@app.route('/deleteWish', methods = ['POST'])
def deleteWish():
	try:
		# print 'mhere'
		if session.get('user_id'):
			Id = request.form['id']
			User = session.get('user_id')

			# print 'mhere1'
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.callproc('sp_deleteWish', (Id, User))
			result = cursor.fetchall()
			# print 'mhere2'
			if len(result) is 0:
				# print 'mhere3'
				conn.commit()
				return json.dumps({'Status':'Ok'})
			else:
				return json.dumps({'Status': 'Error'})
	except Exception as e:
		return render_template('error.html',error = 'Unauthorized Access')
	finally:
		cursor.close()
		conn.close()

@app.route('/upload', methods = ['POST', 'GET'])
def upload():
	if request.method == 'POST':
		file = request.files['file']
		# print file
		extension = os.path.splitext(file.filename)[1]
		# print extension
		f_name = str(uuid.uuid4()) + extension
		# print f_name
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
		return json.dumps({'filename':f_name})

@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')

@app.route('/getAllWishes')
def getAllWishes():
	try:
		if session.get('user_id'):
			User = session.get('user_id')

			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.callproc('sp_getAllWishes',(User,))
			result = cursor.fetchall()

			wishes_dict = []
			for wish in result:
				wish_dict = {
					'Id': wish[0],
					'Title': wish[1],
					'Description': wish[2],
					'FilePath': wish[3],
					'Like': wish[4],
					'HasLiked': wish[5]
				}
				wishes_dict.append(wish_dict)
			return json.dumps(wishes_dict)
		else:
			return render_template('error.html', error = "Unauthorized Access")
	except Exception as e:
		return render_template('error.html', error = str(e))
	finally:
		cursor.close()
		conn.close()
@app.route('/addUpdateLikes', methods = ['POST'])
def addUpdateLikes():
	try:
		if session.get('user_id'):
			WishId = request.form['wish']
			Like = request.form['like']
			User = session.get('user_id')

			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.callproc('sp_addUpdateLikes', (WishId, User, Like))
			data = cursor.fetchall()
			if len(data) is 0:
				conn.commit()
				# data_dict = {
				# 	'Status': 'Ok',
				# 	'Like': Like
				# }
				cursor.close()
				conn.close()

				conn = mysql.connect()
				cursor = conn.cursor()
				cursor.callproc('sp_getLikeStatus', (WishId, User))
				result = cursor.fetchall()

				# data_dict.append({'Total': result[0][0], 'LikeStatus': result[0][1]})
				# print data_dict
				return json.dumps({'Status':'OK','Total':result[0][0],'LikeStatus':result[0][1]})
			else:
				return render_template('error.html',error = 'An error occurred!')
		else:
			return render_template('error.html',error = 'Unauthorized Access')
	except Exception as e:
		return render_template('error.html',error = str(e))
	finally:
		cursor.close()
		conn.close()


if __name__=='__main__':
	app.run(debug=True)