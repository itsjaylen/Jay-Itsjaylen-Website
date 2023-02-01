FROM python:3.11.1


WORKDIR /app
COPY . /app



RUN pip install -r requirements.txt

#TODO ADD PYTHON VENV 
CMD ["gunicorn", "app:create_app()", "-b", "0.0.0.0:8001"]