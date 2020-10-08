import os
import pymongo
import face_recognition
import numpy as np
import cv2
import json
from datetime import datetime


# INITIALIZING DATABASE
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Face_Recognition"]
mycol = mydb["User_Details"]
mycol1 = mydb["in_out"]


# FINDING ALL DOCS IN DATABASE
student_image_encoding_database = mycol.find()


# INITIALIZING LIST FOR NUMPY ARRAY OF FACE ENCODINGS
known_face_encodings = []
known_face_names = []  

# ITERATING EACH DOC IN DATABASE AND APPENDING TO ENCODINGS & NAMES LIST
for doc in student_image_encoding_database:
	
	student_image_encoding_np =np.asarray(doc["student_image_encoding"])
	known_face_encodings.append(student_image_encoding_np)
	known_face_names.append(doc["student_name"])
	

# print(known_face_encodings)
# print(known_face_names)



# FACE RECOGNITION #
# STARTS #
# -------------------HERE-------------------------- #
   
video_capture = cv2.VideoCapture(0)

face_locations=[]
face_encodings=[]
face_names=[]
process_this_frame= True

while True:
    ret, frame =video_capture.read()

    small_frame = cv2.resize(frame, (0,0), fx=1,fy=1)

    rgb_small_frame = small_frame[:, :, ::-1]

    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings =face_recognition.face_encodings(rgb_small_frame,face_locations)

        face_names=[]
       
       
        for face_encoding in face_encodings:
                 
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                in_timestamp = mycol1.update({'$and':[{'student_name' : name},{'in_time':datetime.now().strftime("%m/%d/%Y, %H:%M")}]},{'student_name': name, 'in_time': datetime.now().strftime("%m/%d/%Y, %H:%M")}, upsert=True)

            # FOR UNKNOWN FACES
            

            if name == "Unknown":
                unknown_name = "Unknown"+ str(datetime.now().strftime("%S:%f")[:-3])
                print(unknown_name)
                 

                # ADDING THE FACE ENCODING AND UNKNOWN COUNTER TO LIST
                known_face_encodings.append(face_encoding)
                known_face_names.append(unknown_name)

                # ADDING THE FACE ENCODING AND UNKNOWN COUNTER TO DATABASE
                x = mycol.insert_one({'student_name': unknown_name, 'student_image_encoding': face_encoding.tolist(), 'added_on': datetime.now()})

            face_names.append(name)
          
            

    process_this_frame = not process_this_frame

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 1
        right *= 1
        bottom *= 1
        left *= 1

        cv2.rectangle(frame, (left,top), (right,bottom), (0,0,255), 2)

        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()

# FACE RECOGNITION #
# ENDS #
# -------------------HERE-------------------------- #