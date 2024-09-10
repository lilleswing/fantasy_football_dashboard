FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH="./"

COPY ffootball /

CMD ["python", "ffootball/app.py"]
