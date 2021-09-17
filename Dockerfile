ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}
COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

WORKDIR /usr/app/
RUN mkdir /app
WORKDIR /app
COPY . .
