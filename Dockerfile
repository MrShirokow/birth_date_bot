FROM python:3.10

WORKDIR /usr/src/bot/

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .