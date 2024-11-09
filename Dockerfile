# Use the official Python base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the port on which the Flask app will run
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=app.py
ENV DATABASE_URL=sqlite:///inputs.db

# Set the entrypoint command to run Gunicorn
CMD ["gunicorn", "-w", "4","--log-level=debug", "-b", "0.0.0.0:5000", "app:app"]