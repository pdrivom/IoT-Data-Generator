FROM python:alpine3.15
LABEL name Pedro Marques

ENV PYHTONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt --upgrade pip

RUN mkdir /api
WORKDIR /usr/src/api
COPY ./api .


CMD ["uvicorn","api:v1","--host","0.0.0.0","--port","8000"]
