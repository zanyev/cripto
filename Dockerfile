# Dockerfile
FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN mkdir ./assets

CMD ["sh", "-c", "python async_get_data.py && python oms.py && python email_sender.py"]

