FROM python:3.10.6
FROM ffmpeg:4.4.1


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get install -y ffmpeg
WORKDIR /flask

#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8001", "views:app"]