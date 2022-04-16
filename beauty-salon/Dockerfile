FROM python:3.7-slim
WORKDIR /barber
ENV PYTHONUNBUFFERED True
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY barber/ .