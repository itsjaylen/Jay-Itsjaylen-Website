FROM python:3.11.1


# Set the working directory in the container
WORKDIR /app

# Copy the application files to the working directory
COPY . .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

#TODO ADD PYTHON VENV 
CMD ["gunicorn", "app:create_app()", "-b", "0.0.0.0:8001"]