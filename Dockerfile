FROM python:3.10.6


WORKDIR /app
COPY . /app



RUN pip install -r requirements.txt

#TODO add github workflow
CMD ["gunicorn", "app:create_app()", "-b", "0.0.0.0:7000"]