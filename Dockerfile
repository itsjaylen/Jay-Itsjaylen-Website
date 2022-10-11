FROM python:3.9



COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /flask

CMD [ "python3", "wsgi.py" ]