# syntax=docker/dockerfile:1

FROM python:3.9.16

WORKDIR /

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8080

CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "App.main:create_app()"]
