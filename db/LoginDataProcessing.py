#!/usr/bin/env python
# coding: utf-8

# In[10]:


import pandas as pd
import numpy as np 
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from dbops import DBMan
import time


# In[2]:


class LoginTableUpdate:
    '''
    The face recognition class will update the known face recognition to Raw_Data Table
    Since we have it saving multiple times for a given person 
    We need to clean the data in order to makes sense 
    Hence 
    Boom!!!! 
    We have this simple cleaning algorithm to clean the data and put it in a more presentable fashion 
    So we clean the data by 
    1st: deleting all the duplicates 
    2nd sorting them according to their emp codes  
        Then delete the previous row if the camera number repeats 
    Last: Write them to the database 
    '''
    def __init__(self):
        ## Giving the Database Credentials 
        self.db = DBMan('mariadb','19283','root','12345','LoginDB') 
        self.dataProcessing()
        
    def getMaxTimeStamp(self):
        ## Getting the maximum known time stamp from Login Table
        maxInTime = self.db.fetch("SELECT MAX(InTime) FROM Login")
        maxOutTime = self.db.fetch("SELECT MAX(OutTime) FROM Login")
        Value = max(maxInTime,maxOutTime)
        return(Value)
    
    def ReadDB(self):
        ## Reading from Database where the timestamp is more than the maximum of last known time stamp in 
        ## Login Table
        try :
            df = pd.read_sql("SELECT * FROM Raw_Data WHERE Timestamp >= '%s' " %self.getMaxTimeStamp()[0][0].strftime('%Y-%m-%d %H:%M:%S'), self.db.connect())
            self.db.close()
        except:
            df = pd.read_sql("SELECT * FROM Raw_Data", self.db.connect())
            self.db.close()
        return(df)
    
    def dataProcessing(self):
        ## Code to clean the data 
        df = self.ReadDB()
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df_sort = df.sort_values(by = ['EmpCode','Timestamp'])
        df_sort.reset_index(inplace=True,drop=True)
        for i in range(len(df_sort)-1):
            if (df_sort['Camera_No'][i+1] == df_sort['Camera_No'][i] or  df_sort['Camera_No'][i+1]%2 == df_sort['Camera_No'][i]%2) and df_sort['EmpCode'][i+1] == df_sort['EmpCode'][i]:
                df_sort = df_sort.drop(i)
        df_sort.reset_index(inplace=True, drop=True)

        ## Code oto write the cleaned data into the Database
        for i in range(len(df_sort)):
            try:
                ## Trying weather we have the specific empcode has Camera Number and any last record 
                cam_no = self.db.fetch("SELECT CamID FROM `Login` Where EmpCode = {0} ORDER BY LoginID DESC LIMIT 1".format(df_sort['EmpCode'][i]))[0][0]
                last_ID = self.db.fetch("SELECT LoginID FROM `Login` Where EmpCode = {0} ORDER BY LoginID DESC LIMIT 1".format(df_sort['EmpCode'][i]))[0][0]      
            except:
                ## If no equating the Camera Number to 0 
                cam_no = 0 
                return('DOne')
            finally:          
                ## Then Writing it to the database 
                ## iF CAMERA Number exists and camera number is not equal to zero we update the existing table
                if df_sort["Camera_No"][i]%2 == cam_no%2 and cam_no != 0 :
                    if df_sort['Camera_No'][i]%2 == 0:
                        sql = "UPDATE Login SET CamID = %s, OutTime = %s,Image_Path = %s  WHERE LoginID = %s"
                    else:
                        sql = "UPDATE Login SET CamID = %s, InTime = %s,Image_Path = %s  WHERE LoginID = %s"
                    rows = [(str(df_sort['Camera_No'][i]),str(df_sort['Timestamp'][i]),str(df_sort['Image_Path'][i]),last_ID)]
                ## Else we insert a new row to the Database
                    Sentence = 'Updated'
                else:
                    if df_sort['Camera_No'][i]%2 == 0:
                        sql = "INSERT INTO Login(EmpCode,OutTime, CamID,Image_Path) VALUES (%s,%s,%s,%s)"
                    else :
                        sql = "INSERT INTO Login(EmpCode,InTime, CamID,Image_Path) VALUES (%s,%s,%s,%s)"
                    rows = [(str(df_sort['EmpCode'][i]),str(df_sort['Timestamp'][i]),str(df_sort['Camera_No'][i]),df_sort['Image_Path'][i])]
                    Sentence = 'Inserted'
                self.db.insert(sql,rows)
                print('{0} into Login Table'.format(Sentence))


# In[ ]:


if __name__ == '__main__':
    while True:
        LoginTableUpdate()
        print("Updated at {0}".format(datetime.now().strftime('%H-%M')))
        time.sleep(30)

