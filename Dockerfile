FROM debian:bullseye

RUN apt-get -y update
RUN apt-get -y install python3 pip

WORKDIR stuff
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
COPY ./*.py .
COPY ./stuff ./stuff

#ENTRYPOINT ["python3", "wsgi.py"]
ENTRYPOINT gunicorn stuff:app --bind=0.0.0.0:8080
