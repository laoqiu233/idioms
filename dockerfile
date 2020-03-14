FROM python:3.7
ADD ./www /www
WORKDIR /www
RUN pip install mysql-connector-python flask pypinyin gunicorn
EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]`