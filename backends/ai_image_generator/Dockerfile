FROM rocm/pytorch:latest

WORKDIR /app

COPY app.py requirements.txt /app/

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "app.py"]