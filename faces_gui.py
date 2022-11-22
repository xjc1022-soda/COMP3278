#coding=utf-8
from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QPushButton, QMessageBox, QLabel
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QMenu, QGridLayout, QLCDNumber
from PyQt5.QtGui import QIcon, QPainter, QColor, QFont
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from datetime import datetime, timedelta, time
import urllib
import numpy as np
import mysql.connector
import cv2
import pyttsx3
import pickle
import sys
import PySimpleGUI as sg
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import webbrowser

now = datetime.now()
sg.theme('LightBlue2')

def Exit():
	global now
	cur = datetime.now()
	t = (cur - now).seconds
	sg.popup_no_titlebar(f"You have stayed in the system for {t//60} m {t%60} s")
	exit()

def selectClass(startDate, endDate):
	myconn = mysql.connector.connect(host="localhost", user="root", passwd="Sodaxjc1022!", database="facerecognition")
	cursor = myconn.cursor()
	global current_name
	select = f"""SELECT C.course_id, C.course_information, WEEKDAY(D.date), D.time, D.dur, R.address
FROM Student S, Course C, Attend A, StartDate D, Classroom R
WHERE S.name = '{current_name}'
	AND D.date between '{startDate.strftime("%Y-%m-%d")}' AND '{endDate.strftime("%Y-%m-%d")}'
	AND C.classroom_id = R.classroom_id
	AND S.student_id = A.student_id
	AND C.course_id = A.course_id
	AND C.course_id = D.course_id
ORDER BY WEEKDAY(D.date), D.time"""
	cursor.execute(select)
	result = cursor.fetchall()
	return result

def generateWeek(dt):
	while dt.weekday() != 6:
		dt = dt - timedelta(days=1)
	dtEnd = dt + timedelta(days=6)
	return [dt, dtEnd, dt.strftime("%Y/%m/%d")+' - '+dtEnd.strftime("%Y/%m/%d")]

class Schedule(QWidget):

	def __init__(self):
		super().__init__()
		loadUi("schedule.ui", self)
		self.setFixedSize(650, 680)
		self.setWindowTitle('Weekly Schedule')
		global now
		now = datetime.now()
		global week
		week = generateWeek(now)
		self.label.setText(week[-1])
		self.leftButton.clicked.connect(self.previousWeek)
		self.rightButton.clicked.connect(self.nextWeek)
		self.currentButton.clicked.connect(self.currentWeek)
		self.exitButton.clicked.connect(self.exit)
		self.show()

	def paintEvent(self, event):
		qpainter = QPainter()
		qpainter.begin(self)
		global now
		week = generateWeek(now)
		self.drawSchedule(qpainter, week[0], week[1])
		qpainter.end()

	def drawSchedule(self, qpainter, start, end):

		colors = [QColor("#b83b2c"), QColor("#dba34b"), QColor("#3479ba"), QColor("#498562"),
		QColor("#734587"), QColor("#d35400"), QColor("#2c3e50"), QColor("#16a085"), QColor("#7f8c8d")]

		result = selectClass(start, end)
		map = dict()
		courses = list(set([i[0] for i in result]))
		for i in range(len(courses)):
			map[courses[i]] = colors[i%len(colors)]

		for course_id,course_information,day,t,dur,address in result:

			tpoint = int(t.total_seconds()/60-570)
			zero = datetime(1,1,1,0,0,0)
			classtime = (zero+t).strftime("%H:%M")
			weekday = (day+1)%7

			qpainter.setPen(QColor("#d4d4d4"))
			qpainter.setBrush(map[course_id])
			qpainter.drawRect(weekday*130-125, 100+tpoint, 120, dur)
			qpainter.setPen(QColor("#ffffff"))
			qpainter.setFont(QFont('Courier', 10))
			qpainter.drawText(-125+weekday*130+5, 100+tpoint+15, classtime)
			qpainter.drawText(-125+weekday*130+5, 100+tpoint+30, course_id)
			qpainter.drawText(-125+weekday*130+5, 100+tpoint+45, address)


	def previousWeek(self):
		global now
		now = now - timedelta(days=7)
		self.label.setText(generateWeek(now)[-1])
		self.repaint()

	def nextWeek(self):
		global now
		now = now + timedelta(days=7)
		self.label.setText(generateWeek(now)[-1])
		self.repaint()

	def currentWeek(self):
		global now
		now = datetime.now()
		self.label.setText(generateWeek(now)[-1])
		self.repaint()

	def exit(self):
		msgBox = QMessageBox()
		msgBox.setFont(QFont('Nanum Gothic', 14))
		msgBox.setText("Are you sure you want to exit?")
		msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		reply = msgBox.exec_()
		if reply == QMessageBox.Yes:
			sys.exit(app.exec_())
		else:
			return

def sendEmail(mail_content, receiver_address):
	sender_address = 'comp3278gp@outlook.com'
	password = 'Passw0rd__'
	message = MIMEMultipart()
	message['From'] = sender_address
	message['To'] = receiver_address
	message['Subject'] = 'Class within 1 hour.'
	message.attach(MIMEText(mail_content, 'plain'))
	session = smtplib.SMTP('smtp.office365.com', 587)
	session.starttls()
	session.login(sender_address, password)
	session.sendmail(sender_address, receiver_address, message.as_string())
	session.quit()

def printClass(result, win):
	layout = [[sg.Text('Class within 1 hour:', font='Courier 12')],[sg.Text('      ')]]

	for course_id,course_information,time,address,message,zoom_link,materials_link in result:
		layout.append([sg.Text(f'{course_id} : {course_information}',size=(30,1))])
		layout.append([sg.Text(f'Time : {time}',size=(30,1))])
		layout.append([sg.Text(f'Classroom address : {address}',size=(30,1))])
		layout.append([sg.Text(f'Teacher\'s message : {message}',size=(30,1))])
		layout.append([sg.Text(f'Zoom link : {zoom_link}', enable_events=True, key=f'Link {zoom_link}')])
		layout.append([sg.Text(f'Course materials link : {materials_link}', enable_events=True, key=f'Link {materials_link}')])
		layout.append([sg.Text('')])

	layout.append([sg.Button('Send by email',size=(15, 1), border_width=0),sg.Text('   '),sg.Button('OK', size=(10, 1), border_width=0)])
	win = sg.Window('Attendance System',
						layout,
						alpha_channel=0.8,
						no_titlebar=True,
						grab_anywhere=True)

	while True:
		event, value = win.read()
		if event is None or event == 'OK':
			Exit()
		elif event == 'Send by email':
			s = ""
			for course_id,course_information,time,address,message,zoom_link,materials_link in result:
				s += f'{course_id} : {course_information}\n'
				s += f'Time : {time}\n'
				s += f'Classroom address : {address}\n'
				s += f'Teacher\'s message : {message}\n'
				s += f'Zoom link : {zoom_link}\n'
				s += f'Course materials link : {materials_link}\n'
				s += '\n'
			addr = sg.popup_get_text("Input your email address: ")
			sendEmail(s, addr)
			sg.popup_no_titlebar("Mail sent!")
		elif event.startswith("Link "):
			webbrowser.open(event.split(' ')[1])


# 1 Create database connection
myconn = mysql.connector.connect(host="localhost", user="root", passwd="Sodaxjc1022!", database="facerecognition")
current_day = now.weekday()
current_time = now.strftime("%H:%M:%S")
cursor = myconn.cursor()


#2 Load recognize and read label from model
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("train.yml")

labels = {"person_name": 1}
with open("labels.pickle", "rb") as f:
	labels = pickle.load(f)
	labels = {v: k for k, v in labels.items()}

# create text to speech
engine = pyttsx3.init()
rate = engine.getProperty("rate")
engine.setProperty("rate", 175)

# Define camera and detect face
face_cascade = cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)


# 3 Define pysimplegui setting
layout =  [
    [sg.Text('    Welcome', size=(15,1), font='Courier 60',text_color='#483D8B' ,justification='left')],
    [sg.Text('Confidence', size=(10,1), font='Courier 20',text_color='#483D8B'),sg.Slider(range=(0,100),orientation='h', resolution=1, default_value=0, size=(50,30), key='confidence')],
    [sg.Text('')],
    [sg.Text('')],
    [sg.Text(' '),sg.Button('OK', size=(10, 2), border_width=0), sg.Text(' '),
    sg.Button('Cancel',size=(10, 2), border_width=0)]]
      
win = sg.Window('Attendance System',
        default_element_size=(21,1),
        text_justification='right',
        alpha_channel=0.8, 
        no_titlebar=True, 
        grab_anywhere=True,
        auto_size_text=False).Layout(layout)

event, values = win.Read()
if event is None or event =='Cancel':
	Exit()
args = values
gui_confidence = args["confidence"]
win_started = False

# 4 Open the camera and start face recognition
while True:
	ret, frame = cap.read()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	faces = face_cascade.detectMultiScale(gray, minNeighbors=5)

	for (x, y, w, h) in faces:
		# print(x, w, y, h)
		roi_gray = gray[y:y + h, x:x + w]
		roi_color = frame[y:y + h, x:x + w]
		# predict the id and confidence for faces
		id_, conf = recognizer.predict(roi_gray)
		print(id_,conf)
		# If the face is recognized
		if conf >= gui_confidence:
			# print(id_)
			# print(labels[id_])
			font = cv2.QT_FONT_NORMAL
			id = 0
			id += 1
			name = labels[id_]
			global current_name
			current_name = name
			color = (255, 0, 0)
			stroke = 2
			cv2.putText(frame, name, (x, y), font, 1, color, stroke, cv2.LINE_AA)
			cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), (2))

			# Find the student information in the database.
			select = "SELECT student_id, name, DAY(login_date), MONTH(login_date), YEAR(login_date) FROM Student WHERE name='%s'" % (name)
			name = cursor.execute(select)
			result = cursor.fetchall()
			# print(result)
			data = "error"

			for x in result:
				data = x

			# If the student's information is not found in the database
			if data == "error":
				# the student's data is not in the database
				print("The student", current_name, "is NOT FOUND in the database.")

				# If the student's information is found in the database
			else:
				select = f"SELECT S.login_date, S.login_time FROM Student S WHERE S.name = '{current_name}'"
				cursor.execute(select)
				result = cursor.fetchall()
				for x in result:
					last_date, last_time = x
				sg.popup_no_titlebar(f"Welcome {current_name}!\n\n  Last login time: {last_date} {last_time}\n  Current login time: {now.date()} {current_time}\n")
				update =  "UPDATE Student SET login_date=%s WHERE name=%s"
				val = (now, current_name)
				cursor.execute(update, val)
				update = "UPDATE Student SET login_time=%s WHERE name=%s"
				val = (current_time, current_name)
				cursor.execute(update, val)
				myconn.commit()

				hello = ("Hello ", current_name, "You did attendance today")
				print(hello)
				engine.say(hello)

				select = f"""SELECT C.course_id, C.course_information, D.time, R.address, C.message, C.zoom_link, C.materials_link
FROM Student S, Course C, Classroom R, Attend A, StartDate D
WHERE S.name = '{current_name}'
	AND S.student_id = A.student_id
	AND C.course_id = A.course_id
	AND C.classroom_id = R.classroom_id
	AND C.course_id = D.course_id
	AND WEEKDAY(D.date) = {current_day}
	AND timediff(D.time, '{current_time}') >= 0
	AND timediff(D.time, '{current_time}') <= '01:00:00'
ORDER BY D.time"""
				cursor.execute(select)
				result = cursor.fetchall()
				# print(select)
				# print(result)
				if len(result) == 0:
					app = QApplication(sys.argv)
					ex = Schedule()
					sys.exit(app.exec_())
				else:
					printClass(result, win)


		# If the face is unrecognized
		else:
			color = (255, 0, 0)
			stroke = 2
			font = cv2.QT_FONT_NORMAL
			cv2.putText(frame, "UNKNOWN", (x, y), font, 1, color, stroke, cv2.LINE_AA)
			cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), (2))
			hello = ("Your face is not recognized")
			print(hello)
			engine.say(hello)
			# engine.runAndWait()

	# GUI
	imgbytes = cv2.imencode('.png', frame)[1].tobytes()
	if not win_started:
		win_started = True
		layout = [
			[sg.Text('Attendance System Interface', size=(40,1), font='Courier 20',justification ='center')],
			[sg.Text('-' * 200, size=(40,1),font='Courier 20')],
			[sg.Image(size=(40,1), data=imgbytes, key='_IMAGE_')],
			[sg.Text('-' * 200, size=(40,1),font='Courier 20')],
			[sg.Text('Confidence', font='Courier 10'),
				sg.Slider(range=(0, 100), orientation='h', resolution=1, default_value=0, size=(15, 15), key='confidence'),
				sg.Text(' ' * 30),
				sg.Button('Exit',size=(12, 1), border_width=0)]
		]
		win = sg.Window('Attendance System',
				default_element_size=(14, 1),
				text_justification='right',
				alpha_channel=0.8, 
				no_titlebar=True, 
				grab_anywhere=True,
				keep_on_top=False,
				auto_size_text=False).Layout(layout).Finalize()
		image_elem = win.FindElement('_IMAGE_')
	else:
		image_elem.Update(data=imgbytes)

	event, values = win.Read(timeout=20)
	if event is None or event == 'Exit':
		Exit()
	gui_confidence = values['confidence']


win.Close()
cap.release()
