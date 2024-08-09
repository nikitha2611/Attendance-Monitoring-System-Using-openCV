import cv2
import pickle
import numpy as np
import os
from datetime import datetime

video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

faces_data = []
i = 0

name = input("Enter Your Name: ")
role = input("Are you a student or staff? (student/staff): ").lower()

if role not in ['student', 'staff']:
    print("Invalid role. Please enter 'student' or 'staff'.")
    exit()

details = {'Name': name, 'Role': role}

if role == 'student':
    department = input("Enter your department: ")
    usn = input("Enter your USN: ")
    details.update({'Department': department, 'USN': usn})
else:
    position = input("Enter your position: ")
    details.update({'Position': position})

while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50, 50))
        if len(faces_data) < 100 and i % 10 == 0:
            faces_data.append(resized_img)
        i += 1
        cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)
    cv2.imshow("Frame", frame)
    k = cv2.waitKey(1)
    if k == ord('q') or len(faces_data) == 100:
        break
video.release()
cv2.destroyAllWindows()

faces_data = np.asarray(faces_data)
faces_data = faces_data.reshape(100, -1)

# Save names to pickle file
if 'names.pkl' not in os.listdir('data/'):
    names = [name] * 100
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)
else:
    with open('data/names.pkl', 'rb') as f:
        names = pickle.load(f)
    names.extend([name] * 100)
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)

# Save faces data to pickle file
if 'faces_data.pkl' not in os.listdir('data/'):
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(faces_data, f)
else:
    with open('data/faces_data.pkl', 'rb') as f:
        faces = pickle.load(f)
    faces = np.vstack([faces, faces_data])
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(faces, f)

# Save details to separate pickle file
if role == 'student':
    details_file = 'data/students_details.pkl'
else:
    details_file = 'data/staff_details.pkl'

if os.path.exists(details_file):
    with open(details_file, 'rb') as f:
        details_list = pickle.load(f)
else:
    details_list = []

details_list.append(details)

with open(details_file, 'wb') as f:
    pickle.dump(details_list, f)

print("Details saved successfully.")