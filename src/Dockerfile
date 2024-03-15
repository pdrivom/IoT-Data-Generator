FROM python:3.13.0a4-alpine AS production
LABEL name Pedro Marques

ENV PYHTONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt --upgrade pip
RUN mkdir /api
WORKDIR /usr/src/api
COPY ./api .
CMD ["uvicorn","api:v1","--host","0.0.0.0","--port","8000"]


FROM production as tests
RUN pip install pytest --upgrade pip