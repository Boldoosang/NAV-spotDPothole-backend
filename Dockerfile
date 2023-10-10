# syntax=docker/dockerfile:1

FROM python:3.10.2

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8080 

CMD [ "python3", "manage.py" , "serve"]