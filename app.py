from flask import Flask, render_template, url_for, flash, redirect,request
from flask_navigation import Navigation
from datetime import datetime
from werkzeug.utils import secure_filename
import urllib.request
import os
import pymongo
import face_recognition
import numpy as np
import json
import bson

# INITIALIZING DATABASE
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Face_Recognition"]
mycol = mydb["User_Details"]

UPLOAD_FOLDER = 'C:/Users/2015b/Face Recognition/Unknown'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
nav = Navigation(app)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

nav.Bar('top', [
    nav.Item('Home', 'upload_form'),
    nav.Item('Log', 'log', {'page': 1}),
	nav.Item('Attendance', 'attendance', {'page': 2})
])


@app.route('/')
def upload_form():
	return render_template('form.html')

@app.route('/log/<int:page>')
def log(page):
	student_log = mycol.find()
	return render_template('log.html', page=page, mycol = student_log)	

@app.route("/editUser", methods=['GET'])  
def editUser():
	getUser = mycol.find({"student_name":request.values.get('name')})
	return render_template('edituser.html', data = getUser) 

@app.route("/saveChanges", methods=['GET','POST'])  
def saveChanges():
	getUser = mycol.find({"student_name":request.values.get('name')})
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			student_image = face_recognition.load_image_file(file)
			student_image_encoding = face_recognition.face_encodings(student_image)[0]
			student_image_encoding_list = student_image_encoding.tolist()
			x = mycol.insert_one({'student_name': request.form.get('name'), 'student_image_encoding': student_image_encoding_list})
			flash('File successfully uploaded')
			return redirect('/')
		else:
			flash('Allowed file types are png, jpg, jpeg')
			return redirect(request.url)	

   

@app.route("/delete", methods=['GET'])
def delete():	
	mycol.delete_one({"student_name":request.values.get('name')})
	return redirect('/')

@app.route("/cancel")
def cancel():	
	return render_template('log.html')		

@app.route('/attendance/<int:page>')
def attendance(page):
	return render_template('attendance.html', page=page)	

@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
			# ADDING NAME AND FACE ENCODINGS TO DATABASE
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			student_image = face_recognition.load_image_file(file)
			student_image_encoding = face_recognition.face_encodings(student_image)[0]
			student_image_encoding_list = student_image_encoding.tolist()
			x = mycol.insert({'student_name': request.form.get('name'), 'student_image_encoding': student_image_encoding_list, 'added_on': datetime.now()})
			flash('File successfully uploaded')
			return redirect('/')
            
		else:
			flash('Allowed file types are png, jpg, jpeg')
			return redirect(request.url)			
    
if __name__ == "__main__":
    app.run(debug=True)
