FROM python:3.13

WORKDIR /app

COPY app.py requirements.txt /app/

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "app.py"]