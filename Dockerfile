# Use Python 3.9 slim image as the base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy all files from the current directory into the container's /app directory
COPY . /app

# Install dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run the Flask application
CMD ["sh", "-c", "python ElderBond.py --host=0.0.0.0 --port=5000"]