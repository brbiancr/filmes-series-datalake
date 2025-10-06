FROM python:3

WORKDIR /app

COPY script.py .

RUN pip install boto3
RUN pip install pandas

RUN mkdir /app/data

VOLUME [ "app/data" ]

COPY . .

CMD [ "python", "script.py"]