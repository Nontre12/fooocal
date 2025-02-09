FROM python:3.13

WORKDIR /app

COPY app.py requirements.txt /app/

RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]