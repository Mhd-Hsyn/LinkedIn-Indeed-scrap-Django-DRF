FROM python:3.8.10
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN apt-get update && apt-get install -y xvfb
RUN pip install -r requirements.txt
COPY . /code/