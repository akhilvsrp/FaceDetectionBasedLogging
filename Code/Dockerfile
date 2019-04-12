FROM python:3.6
ARG user
ARG uid
#
ENV USER=${user}
RUN useradd ${user} -u ${uid} -s /bin/bash --no-create-home
#
WORKDIR /Code
#
RUN apt-get -y update
RUN apt-get install -y build-essential cmake
RUN apt-get install -y libopenblas-dev liblapack-dev 
RUN apt-get install -y libx11-dev libgtk-3-dev

RUN pip install numpy
RUN pip install dlib
RUN pip install opencv-python
RUN pip install face_recognition
RUN pip install pandas
RUN pip install pymysql
RUN pip install apscheduler

CMD ["python","-u","./Camera_Recognition.py"]
