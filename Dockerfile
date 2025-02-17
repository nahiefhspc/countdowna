# Use a lightweight Python image
FROM python:3.10-slim

# Set environment variables to ensure the application runs properly
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install the necessary dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . /app/

# Command to run the bot application
CMD ["python3", "main.py"]
