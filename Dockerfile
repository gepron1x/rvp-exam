FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p instance

RUN chmod -R 777 instance

RUN chmod +x entrypoint.sh

EXPOSE 5000

ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./entrypoint.sh"]