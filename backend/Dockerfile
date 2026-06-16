FROM python:3.11-slim

WORKDIR /app

COPY requirements/ requirements/
RUN pip install -r requirements/dev.txt

COPY . .

EXPOSE 8000
