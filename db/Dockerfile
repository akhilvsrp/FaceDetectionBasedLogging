FROM python:3.6

WORKDIR /db

RUN pip install numpy
RUN pip install pandas
RUN pip install pymysql
RUN pip install apscheduler

CMD ["python","-u","./LoginDataProcessing.py"]
