FROM python:3.12-slim

WORKDIR /app

# Dependencies first: this layer is cached and rebuilt only when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tracker/ tracker/

# The database lives in /data so a mounted volume keeps it between container restarts.
ENV TRACKER_DB=/data/tracker.db
RUN mkdir -p /data

EXPOSE 8000
CMD ["uvicorn", "tracker.main:app", "--host", "0.0.0.0", "--port", "8000"]
