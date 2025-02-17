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

# Expose the port (8080) to ensure the health check passes
EXPOSE 8080

# Add a simple health check (this assumes your app is listening on port 8080)
HEALTHCHECK CMD curl --fail http://localhost:8080/health || exit 1

# Command to run the bot application
CMD ["python3", "main.py"]
