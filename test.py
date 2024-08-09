from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

def speak(str1):
    speak = Dispatch("SAPI.SpVoice")
    speak.Speak(str1)

video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Load labels and faces data
with open('data/names.pkl', 'rb') as w:
    LABELS = pickle.load(w)
with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

# Check if the number of faces matches the number of labels
if len(FACES) != len(LABELS):
    raise ValueError(f"Mismatch in number of samples: Faces ({len(FACES)}) and Labels ({len(LABELS)})")

print('Shape of Faces matrix --> ', FACES.shape)

# Train KNN classifier
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

imgBackground = cv2.imread("background.png")

COL_NAMES_STUDENT = ['NAME', 'DEPARTMENT', 'USN', 'TIME']
COL_NAMES_STAFF = ['NAME', 'POSITION', 'TIME']

# Load additional details
students = {}
staff = {}
if os.path.exists('data/students_details.pkl'):
    with open('data/students_details.pkl', 'rb') as f:
        students_list = pickle.load(f)
        for student in students_list:
            students[student['Name']] = student
if os.path.exists('data/staff_details.pkl'):
    with open('data/staff_details.pkl', 'rb') as f:
        staff_list = pickle.load(f)
        for staff_member in staff_list:
            staff[staff_member['Name']] = staff_member

while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
        output = knn.predict(resized_img)
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
        csv_file = f"Attendance/Attendance_{date}.csv"
        exist = os.path.isfile(csv_file)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 2)
        cv2.rectangle(frame, (x, y-60), (x+w, y), (50, 50, 255), -1)

        if output[0] in students:
            details = students[output[0]]
            name = details['Name']
            department = details.get('Department', 'N/A')
            usn = details.get('USN', 'N/A')
            cv2.putText(frame, f"{name} ({usn})", (x, y-45), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
            cv2.putText(frame, department, (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
            attendance = [name, department, usn, timestamp]
            attendance_file = "students_attendance.csv"
            column_names = COL_NAMES_STUDENT
        elif output[0] in staff:
            details = staff[output[0]]
            name = details['Name']
            position = details.get('Position', 'N/A')
            cv2.putText(frame, f"{name} ({position})", (x, y-45), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
            attendance = [name, position, timestamp]
            attendance_file = "staff_attendance.csv"
            column_names = COL_NAMES_STAFF
        else:
            cv2.putText(frame, str(output[0]), (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
            attendance = [str(output[0]), timestamp]
            attendance_file = csv_file
            column_names = COL_NAMES_STUDENT  # Default to student format if unknown

    imgBackground[162:162 + 480, 55:55 + 640] = frame
    cv2.imshow("Frame", imgBackground)
    k = cv2.waitKey(1)
    if k == ord('o'):
        speak("Attendance Taken..")
        time.sleep(5)
        with open(attendance_file, "a", newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not exist:
                writer.writerow(column_names)
            writer.writerow(attendance)
    if k == ord('q'):
        break
video.release()
cv2.destroyAllWindows()
