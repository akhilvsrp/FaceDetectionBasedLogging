#!/usr/bin/env python
# coding: utf-8

# In[3]:


import face_recognition
import cv2
from datetime import datetime 
import time
from dbops import DBMan
import pandas as pd
from multiprocessing import Process


# In[33]:


class Face_Recogniton:
    '''
        Prameters:
            Url = Camera stream Link 
            CameraNumber = Number of the Camera to be updated in the DataBase 
        Function:
            This function will take the Camera Stream from the url and camera number of the stream for DB purposes
            and start live facial recognition 
            To acess the stream we use openCV VideoCapture 
            And also use in house developed DBops or DB operations class for different DB operations 
            Importantly we use the face_recognition library with a tolerance of 0.5 to do facial recognition 
    '''
    def __init__(self,Url,CameraNumber):
        self.db = DBMan('mariadb','19283','root','12345','LoginDB') 
        self.known_face_encodings = []
        self.known_face_EmpCode = []
        self.known_face_names = []
        self.createEncodings()
        self.run_detection(Url,CameraNumber)
    
    
    def createEncodings(self):
        ## Reading Data from the Employee table and create encodings
        df = pd.read_sql('''SELECT * FROM Employee''', self.db.connect())
        self.db.close()
        
        for i in range(len(df)):
            self.known_face_names.append(df['EmpName'][i])
            self.known_face_EmpCode.append(df['EmpCode'][i])
            self.known_face_encodings.append(df['EmpName'][i])
            image = face_recognition.load_image_file(df['Image'][i])

            self.known_face_encodings[-1]= face_recognition.face_encodings(image)[0]
            print('Done Encoding for '+df['EmpName'][i])    
            
    

    def run_detection(self,Url,CameraNumber):
        a = []
        #   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
        #   2. Only detect faces in every other frame of video.

        # Get a reference to webcam #0 (the default one)
        video_capture = cv2.VideoCapture(Url)
        camera = CameraNumber

        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        while True:
            # Grab a single frame of video
            ret, frame = video_capture.read()

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)


                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)

                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding , tolerance=0.5)
                    name = "Unknown"

                    # Write to Disk 
                    image_name = "./Unkown_Frames/{0}-{1}.jpg".format(datetime.now().strftime('%Y%m%d%H%M%S'),name)
                    cv2.imwrite(image_name, frame)
                    
                    sql = '''INSERT INTO UnknownTable(ImagePath, Camera_No) Values (%s,%s)'''
                    # Write to DB
                    self.db.insert(sql,[(image_name, camera)])

                    # If a match was found in known_face_encodings, just use the first one.
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = self.known_face_names[first_match_index]
                        ECode = self.known_face_EmpCode[first_match_index]
                        end = time.time()

                        # Write to Disk 
                        path = "./Frames/{0}-{1}-{2}.jpg".format(datetime.now().strftime('%Y%m%d%H%M%S'),name,ECode)
                        cv2.imwrite(path, frame)
                        
                        sql = '''INSERT INTO Raw_Data(EmpCode, Camera_No, Image_Path) Values (%s,%s,%s)'''

                        # Write to DB 
                        self.db.insert(sql,[(str(ECode),camera,path)])
                        
                    face_names.append(name)
                    print(name + 'updated')            
            # Ignore every alternate Frame
            process_this_frame = not process_this_frame



# In[19]:


url1 = 'rtsp://admin:admin@123@172.16.16.19:554/cam/realmonitor?channel=9&subtype=0'
url2 = 'rtsp://admin:admin@123@172.16.16.19:554/cam/realmonitor?channel=8&subtype=0'


# In[34]:


if __name__ == '__main__':
    proc  = Process(target = Face_Recogniton,args = (url1,1))
    proc2 = Process(target = Face_Recogniton, args = (url2,2))
    proc.start()
    proc2.start()
    
    proc.join()
    proc2.join()

