# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Set environment variable for bot token (you can also use Koyeb secrets for this)
ENV TELEGRAM_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"

# Run the Python script when the container starts
CMD ["python3", "main.py"]
