FROM debian:bullseye

RUN apt-get -y update
RUN apt-get -y install python3 pip

WORKDIR stuff
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
COPY ./stuff ./stuff
COPY ./*.py .

ENTRYPOINT ["python3", "wsgi.py"]
